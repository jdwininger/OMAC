//
//  ImportExportView.swift
//  OMAC
//
//  Created on 2025-11-27
//  View for importing and exporting collection data
//

import SwiftUI
import UniformTypeIdentifiers

struct ImportExportView: View {
    @Environment(\.modelContext) private var modelContext
    @Environment(\.dismiss) private var dismiss

    @StateObject private var importExport = DataImportExport.shared
    @State private var showingImportPicker = false
    @State private var showingExportSuccess = false
    @State private var exportURL: URL?
    @State private var showingError = false
    @State private var errorMessage = ""

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                headerView
                Spacer()
                importSection
                exportSection
                backupSection
                Spacer()
            }
            .padding()
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .fileImporter(
                isPresented: $showingImportPicker,
                allowedContentTypes: [UTType.commaSeparatedText],
                allowsMultipleSelection: false
            ) { result in
                handleImportResult(result)
            }
            .alert("Import/Export Error", isPresented: $showingError) {
                Button("OK", role: .cancel) { }
            } message: {
                Text(errorMessage)
            }
            .alert("Export Successful", isPresented: $showingExportSuccess) {
                Button("OK", role: .cancel) { }
                if let url = exportURL {
                    Button("Show in Finder") {
                        NSWorkspace.shared.selectFile(url.path, inFileViewerRootedAtPath: "")
                    }
                }
            } message: {
                if let url = exportURL {
                    Text("File saved to: \(url.path)")
                }
            }
            .overlay(importProgressOverlay)
        }
    }

    private var headerView: some View {
        VStack(spacing: 20) {
            Text("Import & Export")
                .font(.largeTitle)
                .fontWeight(.bold)

            Text("Import your collection data from CSV files or export your current collection.")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .padding(.horizontal)
        }
    }

    private var importSection: some View {
        VStack(spacing: 16) {
            Text("Import Data")
                .font(.title2)
                .fontWeight(.semibold)

            Text("Import figures from a CSV file. The file should contain columns for name, series, manufacturer, etc.")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .font(.subheadline)

            Button(action: {
                showingImportPicker = true
            }) {
                Label("Import from CSV", systemImage: "square.and.arrow.down")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
            .disabled(importExport.isImporting)
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
    }

    private var exportSection: some View {
        VStack(spacing: 16) {
            Text("Export Data")
                .font(.title2)
                .fontWeight(.semibold)

            Text("Export your entire collection to a CSV file that can be opened in Excel or other spreadsheet applications.")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .font(.subheadline)

            Button(action: {
                Task {
                    do {
                        exportURL = try await importExport.exportToCSV(modelContext: modelContext)
                        showingExportSuccess = true
                    } catch {
                        errorMessage = error.localizedDescription
                        showingError = true
                    }
                }
            }) {
                Label("Export to CSV", systemImage: "square.and.arrow.up")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
    }

    private var backupSection: some View {
        VStack(spacing: 16) {
            Text("Backup & Restore")
                .font(.title2)
                .fontWeight(.semibold)

            Text("Create backups of your collection or restore from a previous backup.")
                .multilineTextAlignment(.center)
                .foregroundColor(.secondary)
                .font(.subheadline)

            HStack(spacing: 12) {
                Button(action: {
                    Task {
                        do {
                            let backupURL = try await importExport.createBackup(modelContext: modelContext)
                            exportURL = backupURL
                            showingExportSuccess = true
                        } catch {
                            errorMessage = error.localizedDescription
                            showingError = true
                        }
                    }
                }) {
                    Label("Create Backup", systemImage: "archivebox")
                        .padding()
                        .background(Color.orange)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }

                Button(action: {
                    showingImportPicker = true
                }) {
                    Label("Restore Backup", systemImage: "arrow.clockwise")
                        .padding()
                        .background(Color.red)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
            }
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
    }

    private var importProgressOverlay: some View {
        Group {
            if importExport.isImporting {
                ZStack {
                    Color.black.opacity(0.4)
                        .edgesIgnoringSafeArea(.all)

                    VStack(spacing: 20) {
                        ProgressView()
                            .scaleEffect(1.5)

                        Text("Importing...")
                            .font(.headline)

                        Text(importExport.importStatus)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)

                        ProgressView(value: importExport.importProgress)
                            .frame(width: 200)
                    }
                    .padding(30)
                    .background(Color.white.opacity(0.95))
                    .cornerRadius(20)
                    .shadow(radius: 10)
                }
            }
        }
    }

    private func handleImportResult(_ result: Result<[URL], Error>) {
        switch result {
        case .success(let urls):
            if let url = urls.first {
                Task {
                    do {
                        try await importExport.importFromCSV(url: url, modelContext: modelContext)
                    } catch {
                        errorMessage = error.localizedDescription
                        showingError = true
                    }
                }
            }
        case .failure(let error):
            errorMessage = error.localizedDescription
            showingError = true
        }
    }
}

#Preview {
    ImportExportView()
}