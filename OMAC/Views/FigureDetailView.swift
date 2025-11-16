import SwiftUI
import CoreData

struct FigureDetailView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var dataManager: DataManager
    
    let figure: ActionFigure
    @State private var isEditing = false
    @State private var showingDeleteAlert = false
    
    // Edit state variables
    @State private var editFigureName = ""
    @State private var editSelectedManufacturer: Manufacturer?
    @State private var editSelectedSeries: Series?
    @State private var editCondition = ""
    @State private var editPricePaid = ""
    @State private var editCurrentValue = ""
    @State private var editNotes = ""
    
    let conditions = ["Mint", "Near Mint", "Excellent", "Very Good", "Good", "Fair", "Poor"]
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    if isEditing {
                        editingView
                    } else {
                        displayView
                    }
                }
                .padding()
            }
            .navigationTitle(figure.figureName ?? "Figure Details")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .primaryAction) {
                    HStack {
                        if isEditing {
                            Button("Cancel") {
                                cancelEditing()
                            }
                            
                            Button("Save") {
                                saveChanges()
                            }
                            .buttonStyle(.borderedProminent)
                        } else {
                            Button("Edit") {
                                startEditing()
                            }
                            
                            Button("Delete") {
                                showingDeleteAlert = true
                            }
                            .foregroundColor(.red)
                        }
                    }
                }
            }
            .alert("Delete Figure", isPresented: $showingDeleteAlert) {
                Button("Cancel", role: .cancel) { }
                Button("Delete", role: .destructive) {
                    dataManager.deleteActionFigure(figure)
                    dismiss()
                }
            } message: {
                Text("Are you sure you want to delete \"\(figure.figureName ?? "this figure")\"? This action cannot be undone.")
            }
        }
    }
    
    // MARK: - Display View
    
    private var displayView: some View {
        VStack(alignment: .leading, spacing: 20) {
            // Basic Information
            Group {
                Text("Basic Information")
                    .font(.title2)
                    .fontWeight(.bold)
                
                InfoRow(label: "Figure Name", value: figure.figureName ?? "Unknown")
                InfoRow(label: "Manufacturer", value: figure.manufacturer?.name ?? "Unknown")
                InfoRow(label: "Series", value: figure.series?.name ?? "Unknown")
                
                if figure.series?.year != 0 {
                    InfoRow(label: "Series Year", value: "\(figure.series?.year ?? 0)")
                }
            }
            
            // Condition and Details
            Group {
                Text("Condition & Details")
                    .font(.title2)
                    .fontWeight(.bold)
                
                InfoRow(label: "Condition", value: figure.condition ?? "Unknown")
                
                if let packaging = figure.packaging {
                    InfoRow(label: "Packaging", value: packaging)
                }
                
                if let height = figure.height, !height.isEmpty {
                    InfoRow(label: "Height", value: height)
                }
                
                if let sku = figure.sku, !sku.isEmpty {
                    InfoRow(label: "SKU", value: sku)
                }
                
                if let upc = figure.upc, !upc.isEmpty {
                    InfoRow(label: "UPC", value: upc)
                }
            }
            
            // Financial Information
            Group {
                Text("Financial Information")
                    .font(.title2)
                    .fontWeight(.bold)
                
                if let pricePaid = figure.pricePaid {
                    InfoRow(label: "Price Paid", value: "$\(pricePaid, formatter: currencyFormatter)")
                }
                
                if let currentValue = figure.currentValue {
                    InfoRow(label: "Current Value", value: "$\(currentValue, formatter: currencyFormatter)")
                }
                
                // Calculate and show profit/loss
                if let pricePaid = figure.pricePaid, let currentValue = figure.currentValue {
                    let difference = currentValue.decimalValue - pricePaid.decimalValue
                    let color: Color = difference >= 0 ? .green : .red
                    let sign = difference >= 0 ? "+" : ""
                    
                    InfoRow(label: "Profit/Loss", value: "\(sign)$\(abs(difference), specifier: "%.2f")", valueColor: color)
                }
            }
            
            // Dates
            Group {
                Text("Dates")
                    .font(.title2)
                    .fontWeight(.bold)
                
                if let purchaseDate = figure.purchaseDate {
                    InfoRow(label: "Purchase Date", value: DateFormatter.shortDate.string(from: purchaseDate))
                }
                
                if let releaseDate = figure.releaseDate {
                    InfoRow(label: "Release Date", value: DateFormatter.shortDate.string(from: releaseDate))
                }
                
                if let dateAdded = figure.dateAdded {
                    InfoRow(label: "Added to Collection", value: DateFormatter.shortDate.string(from: dateAdded))
                }
            }
            
            // Notes
            if let notes = figure.notes, !notes.isEmpty {
                Group {
                    Text("Notes")
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    Text(notes)
                        .font(.body)
                        .padding()
                        .background(Color.gray.opacity(0.1))
                        .cornerRadius(8)
                }
            }
        }
    }
    
    // MARK: - Editing View
    
    private var editingView: some View {
        VStack(alignment: .leading, spacing: 20) {
            Group {
                Text("Basic Information")
                    .font(.title2)
                    .fontWeight(.bold)
                
                VStack(alignment: .leading, spacing: 12) {
                    TextField("Figure Name", text: $editFigureName)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    
                    VStack(alignment: .leading) {
                        Text("Manufacturer")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Picker("Manufacturer", selection: $editSelectedManufacturer) {
                            Text("Select Manufacturer").tag(nil as Manufacturer?)
                            ForEach(dataManager.manufacturers, id: \.id) { manufacturer in
                                Text(manufacturer.name ?? "Unknown").tag(manufacturer as Manufacturer?)
                            }
                        }
                        .pickerStyle(MenuPickerStyle())
                    }
                    
                    VStack(alignment: .leading) {
                        Text("Series")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Picker("Series", selection: $editSelectedSeries) {
                            Text("Select Series").tag(nil as Series?)
                            ForEach(dataManager.series, id: \.id) { series in
                                Text(series.name ?? "Unknown").tag(series as Series?)
                            }
                        }
                        .pickerStyle(MenuPickerStyle())
                    }
                    
                    VStack(alignment: .leading) {
                        Text("Condition")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Picker("Condition", selection: $editCondition) {
                            ForEach(conditions, id: \.self) { condition in
                                Text(condition).tag(condition)
                            }
                        }
                        .pickerStyle(MenuPickerStyle())
                    }
                }
            }
            
            Group {
                Text("Financial Information")
                    .font(.title2)
                    .fontWeight(.bold)
                
                HStack {
                    VStack(alignment: .leading) {
                        Text("Price Paid")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        TextField("0.00", text: $editPricePaid)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                    }
                    
                    VStack(alignment: .leading) {
                        Text("Current Value")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        TextField("0.00", text: $editCurrentValue)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                    }
                }
            }
            
            Group {
                Text("Notes")
                    .font(.title2)
                    .fontWeight(.bold)
                
                TextEditor(text: $editNotes)
                    .frame(minHeight: 100)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                    )
            }
        }
    }
    
    // MARK: - Helper Methods
    
    private func startEditing() {
        editFigureName = figure.figureName ?? ""
        editSelectedManufacturer = figure.manufacturer
        editSelectedSeries = figure.series
        editCondition = figure.condition ?? "Mint"
        editPricePaid = figure.pricePaid?.stringValue ?? ""
        editCurrentValue = figure.currentValue?.stringValue ?? ""
        editNotes = figure.notes ?? ""
        isEditing = true
    }
    
    private func cancelEditing() {
        isEditing = false
    }
    
    private func saveChanges() {
        let pricePaidDecimal = Decimal(string: editPricePaid)
        let currentValueDecimal = Decimal(string: editCurrentValue)
        
        dataManager.updateActionFigure(
            figure,
            name: editFigureName,
            manufacturer: editSelectedManufacturer,
            series: editSelectedSeries,
            condition: editCondition.isEmpty ? nil : editCondition,
            pricePaid: pricePaidDecimal,
            currentValue: currentValueDecimal,
            notes: editNotes.isEmpty ? nil : editNotes
        )
        
        isEditing = false
    }
    
    private var currencyFormatter: NumberFormatter {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        formatter.locale = Locale.current
        return formatter
    }
}

struct InfoRow: View {
    let label: String
    let value: String
    var valueColor: Color = .primary
    
    var body: some View {
        HStack {
            Text("\(label):")
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            Spacer()
            
            Text(value)
                .font(.subheadline)
                .foregroundColor(valueColor)
                .fontWeight(.medium)
        }
        .padding(.vertical, 2)
    }
}



#Preview {
    FigureDetailView(figure: {
        let context = PersistenceController.preview.container.viewContext
        let figure = ActionFigure(context: context)
        figure.figureName = "Spider-Man"
        figure.condition = "Mint"
        return figure
    }())
    .environmentObject(DataManager(context: PersistenceController.preview.container.viewContext))
}