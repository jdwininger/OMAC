import CoreData

class PersistenceController {
    static let shared = PersistenceController()
    
    static var preview: PersistenceController = {
        let controller = PersistenceController(inMemory: true)
        let viewContext = controller.container.viewContext
        
        // Create sample data for previews
        let sampleManufacturer = Manufacturer(context: viewContext)
        sampleManufacturer.id = UUID()
        sampleManufacturer.name = "Hasbro"
        
        let sampleSeries = Series(context: viewContext)
        sampleSeries.id = UUID()
        sampleSeries.name = "Marvel Legends"
        sampleSeries.year = 2023
        sampleSeries.manufacturer = sampleManufacturer
        
        let sampleFigure = ActionFigure(context: viewContext)
        sampleFigure.id = UUID()
        sampleFigure.figureName = "Spider-Man"
        sampleFigure.condition = "Mint"
        sampleFigure.pricePaid = NSDecimalNumber(value: 24.99)
        sampleFigure.currentValue = NSDecimalNumber(value: 35.00)
        sampleFigure.dateAdded = Date()
        sampleFigure.manufacturer = sampleManufacturer
        sampleFigure.series = sampleSeries
        
        do {
            try viewContext.save()
        } catch {
            // Handle error appropriately in a real app
            let nsError = error as NSError
            fatalError("Unresolved error \(nsError), \(nsError.userInfo)")
        }
        
        return controller
    }()
    
    let container: NSPersistentCloudKitContainer
    
    init(inMemory: Bool = false) {
        container = NSPersistentCloudKitContainer(name: "OMAC")
        
        if inMemory {
            container.persistentStoreDescriptions.first!.url = URL(fileURLWithPath: "/dev/null")
        }
        
        // Configure for CloudKit
        container.persistentStoreDescriptions.forEach { storeDescription in
            storeDescription.setOption(true as NSNumber, forKey: NSPersistentHistoryTrackingKey)
            storeDescription.setOption(true as NSNumber, forKey: NSPersistentStoreRemoteChangeNotificationPostOptionKey)
        }
        
        container.loadPersistentStores { _, error in
            if let error = error as NSError? {
                // Handle error appropriately in a real app
                fatalError("Unresolved error \(error), \(error.userInfo)")
            }
        }
        
        container.viewContext.automaticallyMergesChangesFromParent = true
    }
}