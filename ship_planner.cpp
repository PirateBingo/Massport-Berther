#include <QtCore>
#include <QCalendarWidget>
#include <QGridLayout>
#include <QSizePolicy>
#include <QSlider>
#include <QTimeEdit>
#include <QDate>
#include <QTime>
#include <QGroupBox>
#include <QScrollArea>
#include <QPushButton>

const static int constexpr SECS_IN_DAY = 60 * 60 / 1 * 24 / 1;

class Timeline: public QWidget{
	public:	
		Timeline(){
			// Configure widget
			this->setObjectName("Timeline");
			this->setSizePolicy(QSizePolicy::Policy::MinimumExpanding,
                                QSizePolicy::Policy::Maximum);

			// Establish grid layout
			QGridLayout* grid_layout = new QGridLayout(this);
			this->setLayout(grid_layout);

			// Calendar widget
			QCalendarWidget* calendar = new QCalendarWidget(this);
			grid_layout->addWidget(calendar, 0, 0, 1, 3);

			// Time slider widget
			QSlider* slider = new QSlider(this);
			slider->setOrientation(Qt::Orientation::Horizontal);
			slider->setRange(0, SECS_IN_DAY - 1);
			grid_layout->addWidget(slider, 1, 0, 1, 2);

			// Time edit widget
			QTimeEdit* time_edit = new QTimeEdit(this);
			grid_layout->addWidget(time_edit, 1, 2, 1, 1);

			[[maybe_unused]] QDate date = calendar->selectedDate();
			[[maybe_unused]] QTime time = time_edit->time();

			// TODO: Manage signals
		};
};

class Scheduler: public QWidget{
	public:
		Scheduler(){
			this->setObjectName("Scheduler");
			this->setSizePolicy(QSizePolicy::Policy::MinimumExpanding,
                                QSizePolicy::Policy::Preferred);

			// Establish grid layout
			QGridLayout* grid_layout = new QGridLayout(this);
			QGroupBox* group_box = new QGroupBox(this);
			group_box->setLayout(grid_layout);

			QScrollArea* scroll = new QScrollArea(this);
			scroll->setSizePolicy(QSizePolicy::Policy::Minimum,
                                  QSizePolicy::Policy::Expanding);
			scroll->setWidget(group_box);
			scroll->setWidgetResizable(true);

			QVBoxLayout* box_layout = new QVBoxLayout(this);
			box_layout->addWidget(scroll);

			QPushButton* spawn_button = new QPushButton("Add Ship: ", this);
			grid_layout->addWidget(spawn_button, 1, 0, 1, 1);
		};
};
