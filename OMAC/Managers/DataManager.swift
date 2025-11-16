import Foundation
import CoreData
import SwiftUI

class DataManager: ObservableObject {
    private let viewContext: NSManagedObjectContext
    
    @Published var actionFigures: [ActionFigure] = []
    @Published var manufacturers: [Manufacturer] = []
    @Published var series: [Series] = []
    
    init(context: NSManagedObjectContext) {
        self.viewContext = context
        fetchAllData()
    }
    
    // MARK: - Fetch Methods
    
    func fetchAllData() {
        fetchActionFigures()
        fetchManufacturers()
        fetchSeries()
    }
    
    func fetchActionFigures() {
        let request: NSFetchRequest<ActionFigure> = ActionFigure.fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \ActionFigure.figureName, ascending: true)]
        
        do {
            actionFigures = try viewContext.fetch(request)
        } catch {
            print("Error fetching action figures: \(error)")
        }
    }
    
    func fetchManufacturers() {
        let request: NSFetchRequest<Manufacturer> = Manufacturer.fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Manufacturer.name, ascending: true)]
        
        do {
            manufacturers = try viewContext.fetch(request)
        } catch {
            print("Error fetching manufacturers: \(error)")
        }
    }
    
    func fetchSeries() {
        let request: NSFetchRequest<Series> = Series.fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Series.name, ascending: true)]
        
        do {
            series = try viewContext.fetch(request)
        } catch {
            print("Error fetching series: \(error)")
        }
    }
    
    // MARK: - ActionFigure CRUD Operations
    
    func addActionFigure(name: String, manufacturer: Manufacturer?, series: Series?, condition: String?, pricePaid: Decimal?, currentValue: Decimal?, notes: String?) {
        let newFigure = ActionFigure(context: viewContext)
        newFigure.id = UUID()
        newFigure.figureName = name
        newFigure.manufacturer = manufacturer
        newFigure.series = series
        newFigure.condition = condition
        newFigure.pricePaid = pricePaid as NSDecimalNumber?
        newFigure.currentValue = currentValue as NSDecimalNumber?
        newFigure.notes = notes
        newFigure.dateAdded = Date()
        
        saveContext()
        fetchActionFigures()
    }
    
    func updateActionFigure(_ figure: ActionFigure, name: String, manufacturer: Manufacturer?, series: Series?, condition: String?, pricePaid: Decimal?, currentValue: Decimal?, notes: String?) {
        figure.figureName = name
        figure.manufacturer = manufacturer
        figure.series = series
        figure.condition = condition
        figure.pricePaid = pricePaid as NSDecimalNumber?
        figure.currentValue = currentValue as NSDecimalNumber?
        figure.notes = notes
        
        saveContext()
        fetchActionFigures()
    }
    
    func deleteActionFigure(_ figure: ActionFigure) {
        viewContext.delete(figure)
        saveContext()
        fetchActionFigures()
    }
    
    // MARK: - Manufacturer CRUD Operations
    
    func addManufacturer(name: String) {
        let newManufacturer = Manufacturer(context: viewContext)
        newManufacturer.id = UUID()
        newManufacturer.name = name
        
        saveContext()
        fetchManufacturers()
    }
    
    func deleteManufacturer(_ manufacturer: Manufacturer) {
        viewContext.delete(manufacturer)
        saveContext()
        fetchManufacturers()
        fetchActionFigures() // Refresh figures since they may be affected
    }
    
    // MARK: - Series CRUD Operations
    
    func addSeries(name: String, year: Int16?, manufacturer: Manufacturer?) {
        let newSeries = Series(context: viewContext)
        newSeries.id = UUID()
        newSeries.name = name
        newSeries.year = year ?? 0
        newSeries.manufacturer = manufacturer
        
        saveContext()
        fetchSeries()
    }
    
    func deleteSeries(_ series: Series) {
        viewContext.delete(series)
        saveContext()
        fetchSeries()
        fetchActionFigures() // Refresh figures since they may be affected
    }
    
    // MARK: - Search and Filter
    
    func searchActionFigures(searchText: String) -> [ActionFigure] {
        if searchText.isEmpty {
            return actionFigures
        }
        
        return actionFigures.filter { figure in
            figure.figureName?.lowercased().contains(searchText.lowercased()) == true ||
            figure.manufacturer?.name?.lowercased().contains(searchText.lowercased()) == true ||
            figure.series?.name?.lowercased().contains(searchText.lowercased()) == true
        }
    }
    
    func filterActionFigures(by manufacturer: Manufacturer) -> [ActionFigure] {
        return actionFigures.filter { $0.manufacturer == manufacturer }
    }
    
    func filterActionFigures(by series: Series) -> [ActionFigure] {
        return actionFigures.filter { $0.series == series }
    }
    
    // MARK: - Statistics
    
    func totalValue() -> Decimal {
        return actionFigures.reduce(0) { total, figure in
            let value = figure.currentValue?.decimalValue ?? 0
            return total + value
        }
    }
    
    func totalInvested() -> Decimal {
        return actionFigures.reduce(0) { total, figure in
            let price = figure.pricePaid?.decimalValue ?? 0
            return total + price
        }
    }
    
    func figureCount() -> Int {
        return actionFigures.count
    }
    
    // MARK: - Helper Methods
    
    private func saveContext() {
        do {
            try viewContext.save()
        } catch {
            print("Error saving context: \(error)")
        }
    }
    
    func getManufacturer(by name: String) -> Manufacturer? {
        return manufacturers.first { $0.name == name }
    }
    
    func getSeries(by name: String) -> Series? {
        return series.first { $0.name == name }
    }
}