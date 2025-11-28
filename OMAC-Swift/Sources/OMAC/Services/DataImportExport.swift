//
//  DataImportExport.swift
//  OMAC
//
//  Created on 2025-11-27
//  Service for importing and exporting collection data
//

import Foundation
import SwiftUI
import UniformTypeIdentifiers
import SwiftData

enum ImportError: LocalizedError {
    case invalidFormat
    case missingRequiredFields
    case invalidData(String)
    case fileNotFound
    case parsingFailed(String)

    var errorDescription: String? {
        switch self {
        case .invalidFormat:
            return "The file format is not supported."
        case .missingRequiredFields:
            return "Required fields are missing from the data."
        case .invalidData(let field):
            return "Invalid data in field: \(field)"
        case .fileNotFound:
            return "The specified file was not found."
        case .parsingFailed(let reason):
            return "Failed to parse data: \(reason)"
        }
    }
}

enum ExportError: LocalizedError {
    case writeFailed
    case directoryNotAccessible

    var errorDescription: String? {
        switch self {
        case .writeFailed:
            return "Failed to write the export file."
        case .directoryNotAccessible:
            return "Cannot access the export directory."
        }
    }
}

@MainActor
class DataImportExport: ObservableObject {
    static let shared = DataImportExport()

    @Published var isImporting = false
    @Published var importProgress: Double = 0
    @Published var importStatus = ""

    private let dateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
        return formatter
    }()

    // MARK: - CSV Import

    func importFromCSV(url: URL, modelContext: ModelContext) async throws {
        isImporting = true
        importProgress = 0
        importStatus = "Reading file..."

        defer {
            isImporting = false
            importProgress = 0
            importStatus = ""
        }

        // Read CSV file
        let csvString: String
        do {
            csvString = try String(contentsOf: url, encoding: .utf8)
        } catch {
            throw ImportError.fileNotFound
        }

        importStatus = "Parsing CSV data..."
        importProgress = 0.2

        // Parse CSV
        let rows = parseCSV(csvString)
        guard !rows.isEmpty else {
            throw ImportError.invalidFormat
        }

        // Validate headers
        let headers = rows[0]
        guard validateHeaders(headers) else {
            throw ImportError.missingRequiredFields
        }

        importStatus = "Importing \(rows.count - 1) items..."
        importProgress = 0.4

        // Process data rows
        let dataRows = Array(rows.dropFirst())
        var importedCount = 0

        for (index, row) in dataRows.enumerated() {
            do {
                try await importFigure(from: row, headers: headers, modelContext: modelContext)
                importedCount += 1

                importProgress = 0.4 + (Double(index + 1) / Double(dataRows.count)) * 0.6
                importStatus = "Imported \(importedCount) of \(dataRows.count) items..."
            } catch {
                print("Failed to import row \(index + 1): \(error)")
                // Continue with other rows
            }
        }

        importProgress = 1.0
        importStatus = "Import completed! Imported \(importedCount) items."
    }

    private func parseCSV(_ csvString: String) -> [[String]] {
        var rows: [[String]] = []
        var currentRow: [String] = []
        var currentField = ""
        var insideQuotes = false

        for char in csvString {
            switch char {
            case "\"":
                insideQuotes.toggle()
            case ",":
                if insideQuotes {
                    currentField.append(char)
                } else {
                    currentRow.append(currentField.trimmingCharacters(in: .whitespacesAndNewlines))
                    currentField = ""
                }
            case "\n":
                if insideQuotes {
                    currentField.append(char)
                } else {
                    currentRow.append(currentField.trimmingCharacters(in: .whitespacesAndNewlines))
                    rows.append(currentRow)
                    currentRow = []
                    currentField = ""
                }
            default:
                currentField.append(char)
            }
        }

        // Handle last row
        if !currentRow.isEmpty || !currentField.isEmpty {
            currentRow.append(currentField.trimmingCharacters(in: .whitespacesAndNewlines))
            rows.append(currentRow)
        }

        return rows
    }

    private func validateHeaders(_ headers: [String]) -> Bool {
        // Check for required fields (case-insensitive)
        let requiredFields = ["name"]
        let headerSet = Set(headers.map { $0.lowercased() })

        return requiredFields.allSatisfy { headerSet.contains($0) }
    }

    private func importFigure(from row: [String], headers: [String], modelContext: ModelContext) async throws {
        guard row.count == headers.count else {
            throw ImportError.parsingFailed("Row length doesn't match headers")
        }

        // Create dictionary from headers and row data
        var data: [String: String] = [:]
        for (index, header) in headers.enumerated() {
            if index < row.count {
                data[header.lowercased()] = row[index]
            }
        }

        // Extract required fields
        guard let name = data["name"], !name.isEmpty else {
            throw ImportError.missingRequiredFields
        }

        // Create ActionFigure
        let figure = ActionFigure(
            name: name,
            series: data["series"],
            wave: data["wave"],
            manufacturer: data["manufacturer"],
            year: Int(data["year"] ?? ""),
            scale: data["scale"],
            condition: data["condition"],
            purchasePrice: Double(data["purchase_price"] ?? ""),
            currentValue: Double(data["current_value"] ?? ""),
            location: data["location"],
            notes: data["notes"]
        )

        // Parse dates if available
        if let createdStr = data["created_at"],
           let createdDate = dateFormatter.date(from: createdStr) {
            figure.createdAt = createdDate
        }

        if let updatedStr = data["updated_at"],
           let updatedDate = dateFormatter.date(from: updatedStr) {
            figure.updatedAt = updatedDate
        }

        modelContext.insert(figure)

        // Note: Photos would need separate import logic
        // For now, we'll skip photo import as it requires file operations
    }

    // MARK: - CSV Export

    func exportToCSV(modelContext: ModelContext) async throws -> URL {
        // Get all figures
        let descriptor = FetchDescriptor<ActionFigure>(
            sortBy: [SortDescriptor(\ActionFigure.name, order: .forward)]
        )

        let figures = try modelContext.fetch(descriptor)

        // Create CSV content
        var csvContent = """
        name,series,wave,manufacturer,year,scale,condition,purchase_price,current_value,location,notes,created_at,updated_at,photo_count
        """

        for figure in figures {
            let row = [
                escapeCSVField(figure.name),
                escapeCSVField(figure.series ?? ""),
                escapeCSVField(figure.wave ?? ""),
                escapeCSVField(figure.manufacturer ?? ""),
                figure.year.map { String($0) } ?? "",
                escapeCSVField(figure.scale ?? ""),
                escapeCSVField(figure.condition ?? ""),
                figure.purchasePrice.map { String($0) } ?? "",
                figure.currentValue.map { String($0) } ?? "",
                escapeCSVField(figure.location ?? ""),
                escapeCSVField(figure.notes ?? ""),
                dateFormatter.string(from: figure.createdAt),
                dateFormatter.string(from: figure.updatedAt),
                String(figure.photoCount)
            ].joined(separator: ",")

            csvContent += "\n" + row
        }

        // Save to file
        let fileManager = FileManager.default
        let downloadsURL = fileManager.urls(for: .downloadsDirectory, in: .userDomainMask).first!
        let timestamp = dateFormatter.string(from: Date()).replacingOccurrences(of: " ", with: "_").replacingOccurrences(of: ":", with: "-")
        let filename = "omac_collection_\(timestamp).csv"
        let fileURL = downloadsURL.appendingPathComponent(filename)

        try csvContent.write(to: fileURL, atomically: true, encoding: .utf8)

        return fileURL
    }

    private func escapeCSVField(_ field: String) -> String {
        if field.contains(",") || field.contains("\"") || field.contains("\n") {
            let escaped = field.replacingOccurrences(of: "\"", with: "\"\"")
            return "\"\(escaped)\""
        }
        return field
    }

    // MARK: - Collection Merging

    func mergeCollections(from url: URL, into modelContext: ModelContext) async throws {
        // This would import from another OMAC collection
        // For now, we'll treat it the same as CSV import
        try await importFromCSV(url: url, modelContext: modelContext)
    }

    // MARK: - Backup/Restore

    func createBackup(modelContext: ModelContext) async throws -> URL {
        // Export to CSV
        let csvURL = try await exportToCSV(modelContext: modelContext)

        // Create backup directory
        let fileManager = FileManager.default
        let appSupport = try fileManager.url(for: .applicationSupportDirectory,
                                           in: .userDomainMask,
                                           appropriateFor: nil,
                                           create: true)
        let omacDir = appSupport.appendingPathComponent("OMAC")
        let backupsDir = omacDir.appendingPathComponent("backups")
        try fileManager.createDirectory(at: backupsDir, withIntermediateDirectories: true)

        // Create backup filename with timestamp
        let timestamp = dateFormatter.string(from: Date()).replacingOccurrences(of: " ", with: "_").replacingOccurrences(of: ":", with: "-")
        let backupFilename = "omac_backup_\(timestamp).csv"
        let backupURL = backupsDir.appendingPathComponent(backupFilename)

        // Copy CSV to backup location
        try fileManager.copyItem(at: csvURL, to: backupURL)

        return backupURL
    }

    func restoreFromBackup(url: URL, modelContext: ModelContext) async throws {
        // Clear existing data first
        try clearAllData(modelContext: modelContext)

        // Import from backup
        try await importFromCSV(url: url, modelContext: modelContext)
    }

    private func clearAllData(modelContext: ModelContext) throws {
        // Delete all figures (photos will be cascade deleted)
        let figures = try modelContext.fetch(FetchDescriptor<ActionFigure>())
        for figure in figures {
            modelContext.delete(figure)
        }

        // Delete all wishlist items
        let wishlistItems = try modelContext.fetch(FetchDescriptor<WishlistItem>())
        for item in wishlistItems {
            modelContext.delete(item)
        }

        try modelContext.save()
    }
}