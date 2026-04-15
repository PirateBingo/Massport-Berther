#include <QtCore>
#include <QtWidgets>

#pragma once

// New model with two columns
class ShipModel: public QStandardItemModel{
	public:
	ShipModel(QObject* parent): QStandardItemModel(0, 2, parent){
		QStringList s = {"", ""};
		this->setHorizontalHeaderLabels(s);
	};
};

class ShipView: public QTreeView{
	public:
	ShipView(){
		// Initialize
		this->setObjectName("Editor");

		// Initialize model and delegate
		this->setModel(new ShipModel(this->parent()));

		// Drag and drop behaviors
		this->setDragEnabled(true);
		this->setAcceptDrops(false);
		this->setDropIndicatorShown(true);

		// Selection behaviors
		this->setSelectionBehavior(this->SelectionBehavior::SelectRows);
		this->setSelectionMode(this->SelectionMode::SingleSelection);
		this->setEditTriggers(this->EditTrigger::DoubleClicked);
	};
};
