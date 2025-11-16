import SwiftUI
import CoreData

struct AddFigureView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var dataManager: DataManager
    
    @State private var figureName = ""
    @State private var selectedManufacturer: Manufacturer?
    @State private var selectedSeries: Series?
    @State private var condition = "Mint"
    @State private var pricePaid = ""
    @State private var currentValue = ""
    @State private var notes = ""
    @State private var height = ""
    @State private var sku = ""
    @State private var upc = ""
    @State private var releaseDate = Date()
    @State private var purchaseDate = Date()
    @State private var packaging = "Carded"
    
    @State private var showingManufacturerAlert = false
    @State private var showingSeriesAlert = false
    @State private var newManufacturerName = ""
    @State private var newSeriesName = ""
    @State private var newSeriesYear = ""
    
    let conditions = ["Mint", "Near Mint", "Excellent", "Very Good", "Good", "Fair", "Poor"]
    let packagingTypes = ["Carded", "Boxed", "Loose", "Blister Pack"]
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Basic Information
                    Group {
                        Text("Basic Information")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        VStack(alignment: .leading, spacing: 12) {
                            TextField("Figure Name *", text: $figureName)
                                .textFieldStyle(RoundedBorderTextFieldStyle())
                            
                            // Manufacturer Selection
                            HStack {
                                VStack(alignment: .leading) {
                                    Text("Manufacturer")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    
                                    Picker("Manufacturer", selection: $selectedManufacturer) {
                                        Text("Select Manufacturer").tag(nil as Manufacturer?)
                                        ForEach(dataManager.manufacturers, id: \.id) { manufacturer in
                                            Text(manufacturer.name ?? "Unknown").tag(manufacturer as Manufacturer?)
                                        }
                                    }
                                    .pickerStyle(MenuPickerStyle())
                                }
                                
                                Button("Add New") {
                                    showingManufacturerAlert = true
                                }
                                .buttonStyle(.borderless)
                            }
                            
                            // Series Selection
                            HStack {
                                VStack(alignment: .leading) {
                                    Text("Series")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    
                                    Picker("Series", selection: $selectedSeries) {
                                        Text("Select Series").tag(nil as Series?)
                                        ForEach(dataManager.series, id: \.id) { series in
                                            Text(series.name ?? "Unknown").tag(series as Series?)
                                        }
                                    }
                                    .pickerStyle(MenuPickerStyle())
                                }
                                
                                Button("Add New") {
                                    showingSeriesAlert = true
                                }
                                .buttonStyle(.borderless)
                            }
                        }
                    }
                    
                    // Condition and Packaging
                    Group {
                        Text("Condition & Packaging")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        VStack(alignment: .leading, spacing: 12) {
                            VStack(alignment: .leading) {
                                Text("Condition")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                
                                Picker("Condition", selection: $condition) {
                                    ForEach(conditions, id: \.self) { condition in
                                        Text(condition).tag(condition)
                                    }
                                }
                                .pickerStyle(MenuPickerStyle())
                            }
                            
                            VStack(alignment: .leading) {
                                Text("Packaging")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                
                                Picker("Packaging", selection: $packaging) {
                                    ForEach(packagingTypes, id: \.self) { type in
                                        Text(type).tag(type)
                                    }
                                }
                                .pickerStyle(MenuPickerStyle())
                            }
                        }
                    }
                    
                    // Financial Information
                    Group {
                        Text("Financial Information")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        VStack(alignment: .leading, spacing: 12) {
                            HStack {
                                VStack(alignment: .leading) {
                                    Text("Price Paid")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    TextField("0.00", text: $pricePaid)
                                        .textFieldStyle(RoundedBorderTextFieldStyle())
                                }
                                
                                VStack(alignment: .leading) {
                                    Text("Current Value")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    TextField("0.00", text: $currentValue)
                                        .textFieldStyle(RoundedBorderTextFieldStyle())
                                }
                            }
                            
                            HStack {
                                VStack(alignment: .leading) {
                                    Text("Purchase Date")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    DatePicker("Purchase Date", selection: $purchaseDate, displayedComponents: .date)
                                        .labelsHidden()
                                }
                                
                                VStack(alignment: .leading) {
                                    Text("Release Date")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                    DatePicker("Release Date", selection: $releaseDate, displayedComponents: .date)
                                        .labelsHidden()
                                }
                            }
                        }
                    }
                    
                    // Additional Details
                    Group {
                        Text("Additional Details")
                            .font(.title2)
                            .fontWeight(.bold)
                        
                        VStack(alignment: .leading, spacing: 12) {
                            TextField("Height (e.g., 6 inches)", text: $height)
                                .textFieldStyle(RoundedBorderTextFieldStyle())
                            
                            TextField("SKU/Item Number", text: $sku)
                                .textFieldStyle(RoundedBorderTextFieldStyle())
                            
                            TextField("UPC/Barcode", text: $upc)
                                .textFieldStyle(RoundedBorderTextFieldStyle())
                            
                            VStack(alignment: .leading) {
                                Text("Notes")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                
                                TextEditor(text: $notes)
                                    .frame(minHeight: 100)
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 8)
                                            .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                                    )
                            }
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("Add Action Figure")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        saveFigure()
                    }
                    .disabled(figureName.isEmpty)
                }
            }
            .alert("Add Manufacturer", isPresented: $showingManufacturerAlert) {
                TextField("Manufacturer Name", text: $newManufacturerName)
                Button("Cancel") {
                    newManufacturerName = ""
                }
                Button("Add") {
                    if !newManufacturerName.isEmpty {
                        dataManager.addManufacturer(name: newManufacturerName)
                        newManufacturerName = ""
                    }
                }
            }
            .alert("Add Series", isPresented: $showingSeriesAlert) {
                TextField("Series Name", text: $newSeriesName)
                TextField("Year", text: $newSeriesYear)
                Button("Cancel") {
                    newSeriesName = ""
                    newSeriesYear = ""
                }
                Button("Add") {
                    if !newSeriesName.isEmpty {
                        let year = Int16(newSeriesYear) ?? 0
                        dataManager.addSeries(name: newSeriesName, year: year, manufacturer: selectedManufacturer)
                        newSeriesName = ""
                        newSeriesYear = ""
                    }
                }
            }
        }
    }
    
    private func saveFigure() {
        let pricePaidDecimal = Decimal(string: pricePaid)
        let currentValueDecimal = Decimal(string: currentValue)
        
        dataManager.addActionFigure(
            name: figureName,
            manufacturer: selectedManufacturer,
            series: selectedSeries,
            condition: condition.isEmpty ? nil : condition,
            pricePaid: pricePaidDecimal,
            currentValue: currentValueDecimal,
            notes: notes.isEmpty ? nil : notes
        )
        
        dismiss()
    }
}

#Preview {
    AddFigureView()
        .environmentObject(DataManager(context: PersistenceController.preview.container.viewContext))
}