import SwiftUI

@main
struct OMACApp: App {
    let persistenceController = PersistenceController.shared
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.managedObjectContext, persistenceController.container.viewContext)
                .environmentObject(DataManager(context: persistenceController.container.viewContext))
        }
    }
}