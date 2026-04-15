#include <QtCore>
#include <QtWidgets>

#include <filesystem>
#include <iostream>

#include "ship_editor.cpp"
#include "ship_map.cpp"
#include "ship_planner.cpp"
#include "ship.cpp"

const static constexpr char* PROGRAM_NAME = "Flynn Cruiseport Planner";

// TODO: Implement icons
auto get_icon = [](char* s){
std::cout << std::filesystem::current_path() << "icons" << s << ".png" << std::endl; };

class Window: QMainWindow{
	public:
		Window(){
			// Customization
			this->setWindowTitle(PROGRAM_NAME);

			// Palette creation
			QPalette* palette = new QPalette;
			QColor* color1 = new QColor(0, 57, 168);
			QColor* color2 = new QColor(color1->lighter().rgb());
			palette->setColor(QPalette::AlternateBase, *color1);
			palette->setColor(QPalette::Accent, *color2);
			palette->setColor(QPalette::Highlight, *color2);
			palette->setColor(QPalette::Light, *color2);
			this->setPalette(*palette);

			// Add widgets
			ShipMap* ship_map = new ShipMap(this);
			this->setCentralWidget(ship_map);

			ShipView* ship_view = new ShipView();
			Timeline* timeline = new Timeline;
			Scheduler* scheduler = new Scheduler;
			dock_widget(ship_view, Qt::LeftDockWidgetArea);
			dock_widget(timeline, Qt::RightDockWidgetArea);
			dock_widget(scheduler, Qt::RightDockWidgetArea);

			// DEBUG
			// Add test ship
			[[maybe_unused]] Ship::Ship* ship = new Ship::Ship(ship_view);

			// Show the result
			this->show();
		};

		// Shorthand for adding dock widgets to the main window
		inline void dock_widget(QWidget* widget, Qt::DockWidgetArea area){
			QDockWidget* dock_widget = new QDockWidget;
			dock_widget->setWidget(widget);
			return this->addDockWidget(area, dock_widget);
		};
};

// Execute program as instance of window class
int main(int argc, char *argv[]){
	QApplication* app = new QApplication(argc, argv);
	[[maybe_unused]] Window* window = new Window;
	return app->exec();
};
