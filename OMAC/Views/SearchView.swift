import SwiftUI
import CoreData

struct SearchView: View {
    @EnvironmentObject private var dataManager: DataManager
    @State private var searchText = ""
    @State private var selectedManufacturer: Manufacturer?
    @State private var selectedSeries: Series?
    @State private var sortOption: SortOption = .name
    @State private var isAscending = true
    
    enum SortOption: String, CaseIterable {
        case name = "Name"
        case manufacturer = "Manufacturer"
        case series = "Series"
        case condition = "Condition"
        case pricePaid = "Price Paid"
        case currentValue = "Current Value"
        case dateAdded = "Date Added"
    }
    
    var filteredAndSortedFigures: [ActionFigure] {
        var figures = dataManager.actionFigures
        
        // Apply text search filter
        if !searchText.isEmpty {
            figures = figures.filter { figure in
                figure.figureName?.lowercased().contains(searchText.lowercased()) == true ||
                figure.manufacturer?.name?.lowercased().contains(searchText.lowercased()) == true ||
                figure.series?.name?.lowercased().contains(searchText.lowercased()) == true ||
                figure.condition?.lowercased().contains(searchText.lowercased()) == true
            }
        }
        
        // Apply manufacturer filter
        if let manufacturer = selectedManufacturer {
            figures = figures.filter { $0.manufacturer == manufacturer }
        }
        
        // Apply series filter
        if let series = selectedSeries {
            figures = figures.filter { $0.series == series }
        }
        
        // Apply sorting
        figures.sort { figure1, figure2 in
            let result: Bool
            
            switch sortOption {
            case .name:
                result = (figure1.figureName ?? "") < (figure2.figureName ?? "")
            case .manufacturer:
                result = (figure1.manufacturer?.name ?? "") < (figure2.manufacturer?.name ?? "")
            case .series:
                result = (figure1.series?.name ?? "") < (figure2.series?.name ?? "")
            case .condition:
                result = (figure1.condition ?? "") < (figure2.condition ?? "")
            case .pricePaid:
                let price1 = figure1.pricePaid?.decimalValue ?? 0
                let price2 = figure2.pricePaid?.decimalValue ?? 0
                result = price1 < price2
            case .currentValue:
                let value1 = figure1.currentValue?.decimalValue ?? 0
                let value2 = figure2.currentValue?.decimalValue ?? 0
                result = value1 < value2
            case .dateAdded:
                let date1 = figure1.dateAdded ?? Date.distantPast
                let date2 = figure2.dateAdded ?? Date.distantPast
                result = date1 < date2
            }
            
            return isAscending ? result : !result
        }
        
        return figures
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Search and Filter Controls
                VStack(spacing: 16) {
                    // Search Text Field
                    HStack {
                        Image(systemName: "magnifyingglass")
                            .foregroundColor(.secondary)
                        
                        TextField("Search figures, manufacturers, series...", text: $searchText)
                            .textFieldStyle(PlainTextFieldStyle())
                        
                        if !searchText.isEmpty {
                            Button(action: { searchText = "" }) {
                                Image(systemName: "xmark.circle.fill")
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(10)
                    
                    // Filter Controls
                    HStack {
                        // Manufacturer Filter
                        VStack(alignment: .leading) {
                            Text("Manufacturer")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            Picker("Manufacturer", selection: $selectedManufacturer) {
                                Text("All Manufacturers").tag(nil as Manufacturer?)
                                ForEach(dataManager.manufacturers, id: \.id) { manufacturer in
                                    Text(manufacturer.name ?? "Unknown").tag(manufacturer as Manufacturer?)
                                }
                            }
                            .pickerStyle(MenuPickerStyle())
                        }
                        
                        // Series Filter
                        VStack(alignment: .leading) {
                            Text("Series")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            Picker("Series", selection: $selectedSeries) {
                                Text("All Series").tag(nil as Series?)
                                ForEach(dataManager.series, id: \.id) { series in
                                    Text(series.name ?? "Unknown").tag(series as Series?)
                                }
                            }
                            .pickerStyle(MenuPickerStyle())
                        }
                        
                        Spacer()
                    }
                    
                    // Sort Controls
                    HStack {
                        VStack(alignment: .leading) {
                            Text("Sort By")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            Picker("Sort By", selection: $sortOption) {
                                ForEach(SortOption.allCases, id: \.self) { option in
                                    Text(option.rawValue).tag(option)
                                }
                            }
                            .pickerStyle(MenuPickerStyle())
                        }
                        
                        Button(action: { isAscending.toggle() }) {
                            Image(systemName: isAscending ? "arrow.up" : "arrow.down")
                                .foregroundColor(.accentColor)
                        }
                        .buttonStyle(BorderlessButtonStyle())
                        
                        Spacer()
                        
                        // Clear Filters Button
                        Button("Clear Filters") {
                            searchText = ""
                            selectedManufacturer = nil
                            selectedSeries = nil
                        }
                        .buttonStyle(.bordered)
                        .disabled(searchText.isEmpty && selectedManufacturer == nil && selectedSeries == nil)
                    }
                }
                .padding()
                .background(Color(.controlBackgroundColor))
                
                Divider()
                
                // Results
                VStack {
                    // Results Count
                    HStack {
                        Text("\(filteredAndSortedFigures.count) figure\(filteredAndSortedFigures.count == 1 ? "" : "s")")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                        
                        Spacer()
                    }
                    .padding(.horizontal)
                    .padding(.top, 8)
                    
                    // Figures List
                    if filteredAndSortedFigures.isEmpty {
                        VStack(spacing: 16) {
                            Image(systemName: "magnifyingglass")
                                .font(.system(size: 48))
                                .foregroundColor(.secondary)
                            
                            Text("No figures found")
                                .font(.title2)
                                .fontWeight(.medium)
                            
                            Text("Try adjusting your search criteria or filters")
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.center)
                        }
                        .padding(.vertical, 60)
                        
                        Spacer()
                    } else {
                        List(filteredAndSortedFigures, id: \.id) { figure in
                            SearchResultRow(figure: figure)
                        }
                        .listStyle(PlainListStyle())
                    }
                }
            }
            .navigationTitle("Search & Filter")
        }
    }
}

struct SearchResultRow: View {
    let figure: ActionFigure
    @State private var showingDetail = false
    @EnvironmentObject private var dataManager: DataManager
    
    var body: some View {
        Button(action: { showingDetail = true }) {
            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 4) {
                    Text(figure.figureName ?? "Unknown Figure")
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    HStack {
                        if let manufacturer = figure.manufacturer?.name {
                            Label(manufacturer, systemImage: "building.2")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        
                        if let series = figure.series?.name {
                            Label(series, systemImage: "tv")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    
                    if let condition = figure.condition {
                        Label("Condition: \(condition)", systemImage: "star")
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
                            .foregroundColor(.primary)
                    }
                    
                    if let pricePaid = figure.pricePaid {
                        Text("Paid: $\(pricePaid, formatter: currencyFormatter)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    if let dateAdded = figure.dateAdded {
                        Text("Added: \(dateAdded, formatter: .shortDate)")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding(.vertical, 4)
        }
        .buttonStyle(PlainButtonStyle())
        .sheet(isPresented: $showingDetail) {
            FigureDetailView(figure: figure)
                .environmentObject(dataManager)
        }
    }
    
    private var currencyFormatter: NumberFormatter {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.locale = Locale.current
        return formatter
    }
}

extension DateFormatter {
    static let shortDate: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        return formatter
    }()
}

#Preview {
    SearchView()
        .environmentObject(DataManager(context: PersistenceController.preview.container.viewContext))
}