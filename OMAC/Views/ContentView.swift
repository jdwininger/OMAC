import SwiftUI
import CoreData

struct ContentView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @EnvironmentObject private var dataManager: DataManager
    @State private var searchText = ""
    @State private var showingAddView = false
    @State private var selectedFigure: ActionFigure?
    @State private var showingDetailView = false
    
    var filteredFigures: [ActionFigure] {
        dataManager.searchActionFigures(searchText: searchText)
    }
    
    var body: some View {
        NavigationSplitView {
            VStack {
                // Search Bar
                HStack {
                    TextField("Search figures...", text: $searchText)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    
                    Button("Add Figure") {
                        showingAddView = true
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()
                
                // Statistics Bar
                HStack {
                    VStack {
                        Text("\(dataManager.figureCount())")
                            .font(.title2)
                            .fontWeight(.bold)
                        Text("Figures")
                            .font(.caption)
                    }
                    
                    Spacer()
                    
                    VStack {
                        Text("$\(dataManager.totalInvested() as NSDecimalNumber, formatter: currencyFormatter)")
                            .font(.title2)
                            .fontWeight(.bold)
                        Text("Invested")
                            .font(.caption)
                    }
                    
                    Spacer()
                    
                    VStack {
                        Text("$\(dataManager.totalValue() as NSDecimalNumber, formatter: currencyFormatter)")
                            .font(.title2)
                            .fontWeight(.bold)
                        Text("Current Value")
                            .font(.caption)
                    }
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(10)
                .padding(.horizontal)
                
                // Figures List
                List(filteredFigures, id: \.id, selection: $selectedFigure) { figure in
                    FigureRowView(figure: figure)
                        .onTapGesture {
                            selectedFigure = figure
                            showingDetailView = true
                        }
                }
                .listStyle(PlainListStyle())
            }
            .navigationTitle("OMAC")
            .sheet(isPresented: $showingAddView) {
                AddFigureView()
                    .environmentObject(dataManager)
            }
            .sheet(isPresented: $showingDetailView) {
                if let figure = selectedFigure {
                    FigureDetailView(figure: figure)
                        .environmentObject(dataManager)
                }
            }
            
        } detail: {
            if let selectedFigure = selectedFigure {
                FigureDetailView(figure: selectedFigure)
                    .environmentObject(dataManager)
            } else {
                Text("Select a figure to view details")
                    .foregroundColor(.gray)
            }
        }
        .onAppear {
            dataManager.fetchAllData()
        }
    }
    
    private var currencyFormatter: NumberFormatter {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.locale = Locale.current
        return formatter
    }
}

struct FigureRowView: View {
    let figure: ActionFigure
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(figure.figureName ?? "Unknown Figure")
                    .font(.headline)
                
                HStack {
                    if let manufacturer = figure.manufacturer?.name {
                        Text(manufacturer)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    
                    if let series = figure.series?.name {
                        Text("• \(series)")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
                
                if let condition = figure.condition {
                    Text("Condition: \(condition)")
                        .font(.caption)
                        .foregroundColor(.blue)
                }
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                if let currentValue = figure.currentValue {
                    Text("$\(currentValue, formatter: currencyFormatter)")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                }
                
                if let pricePaid = figure.pricePaid {
                    Text("Paid: $\(pricePaid, formatter: currencyFormatter)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(.vertical, 4)
    }
    
    private var currencyFormatter: NumberFormatter {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.locale = Locale.current
        return formatter
    }
}

#Preview {
    ContentView()
        .environment(\.managedObjectContext, PersistenceController.preview.container.viewContext)
        .environmentObject(DataManager(context: PersistenceController.preview.container.viewContext))
}