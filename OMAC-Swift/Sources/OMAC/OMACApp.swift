//
//  OMACApp.swift
//  OMAC
//
//  Created on 2025-11-27
//  One 'Mazing ActionFigure Catalog - Swift Version
//

import SwiftUI

@main
struct OMACApp: App {
    let persistenceController = PersistenceController.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .modelContainer(persistenceController.container)
        }
        .windowStyle(.titleBar)
        .windowToolbarStyle(.unified(showsTitle: true))
        .commands {
            SidebarCommands()
        }
    }
}