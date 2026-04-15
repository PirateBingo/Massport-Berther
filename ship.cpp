#include <QtCore>
#include <QtWidgets>

#include "ship.hpp"
#include "ship_editor.cpp"

const constexpr QSize ICON_SIZE = QSize(32, 32);
const constexpr QIcon::State ICON_STATE = QIcon::On;
const constexpr QIcon::Mode ICON_MODE = QIcon::Active;

// Create simplistic icon out of pattern, color or both
class IconEngine: public QIconEngine{
	public:
	IconEngine(QColor color){ 
		brush = QBrush(color, Qt::SolidPattern);
	};
	IconEngine(Qt::BrushStyle style){
		brush = QBrush(Qt::black, style);
	};
	IconEngine(QColor color, Qt::BrushStyle style){
		brush = QBrush(color, style);
	};
	QIcon get_icon(){ return QIcon(this); };

	private:
	QBrush brush;
	void paint(QPainter* painter, const QRect &rect,
	[[maybe_unused]] QIcon::Mode mode = ICON_MODE,
	[[maybe_unused]] QIcon::State state = ICON_STATE) override final{
		painter->fillRect(rect, this->brush);
	};
	// FIXME Renders incorrectly
	QPixmap pixmap(const QSize& size = ICON_SIZE, 
	QIcon::Mode mode = ICON_MODE,
	QIcon::State state = ICON_STATE) override final{
		QPixmap pixmap = QPixmap(size);
		pixmap.fill(Qt::transparent);
		QPainter painter(&pixmap);
		paint(&painter, QRect(QPoint(0, 0), size), mode, state);
		return pixmap;
	};
	QIconEngine* clone() const override final{
		return new IconEngine(*this);
	};
};

// Uniform random generator for colors and patterns
int randint(int range){
	std::random_device rd;
	std::mt19937 gen(rd());
	std::uniform_int_distribution<> distrib(1, range);
	return distrib(gen);
};

namespace Ship{
	// Pattern widget used to select drawing style for ships
	class PatternSelect: public QComboBox{
		public:
		PatternSelect(QWidget* widget): QComboBox(widget){
			// Retrieve patterns and assign them to their respective items
			for(std::size_t i = 0; i < PATTERN_ARRAY.size(); ++i){
				IconEngine* icon_engine = new IconEngine(PATTERN_ARRAY[i].first);
				QIcon icon = icon_engine->get_icon();
				insertItem(i, icon, PATTERN_ARRAY[i].second);
			}
		};
	};

	template <class WidgetType>
	class Delegate: public QStyledItemDelegate{
		public:
		Delegate(): QStyledItemDelegate(){};

		// Create new widget of type
		QWidget* createEditor(QWidget* parent,
		[[maybe_unused]] const QStyleOptionViewItem& option,
		[[maybe_unused]] const QModelIndex& index) const override{
			WidgetType* widget = new WidgetType(parent);
			return widget;
		};

		protected:
		virtual void init_widget(QWidget* editor) const = 0;
	};

	// BASE ITEM DEFINITION
	template <class WidgetType, typename T>
	class Item: public Delegate<WidgetType>{
		public:
		Item(ShipView* view, QStandardItem* ship, QString name = ""): Delegate<WidgetType>(){
			this->left = new QStandardItem(name);
			this->left->setFlags(static_cast<Qt::ItemFlags>(LABEL_FLAGS));
			this->right = new QStandardItem();

			int row_count = ship->rowCount();
			ship->setChild(row_count, 0, left);
			ship->setChild(row_count, 1, right);

			view->setItemDelegateForRow(right->index().row(), this);
		};

		protected:
		virtual bool check() = 0;

		// 1. Static cast the editor, assign it to a widget alias
		// 2. Connect commitData signal
		// 3. Const cast this item, assign it to type alias
		// 4. Check the item
		virtual void init_widget(QWidget* editor) const = 0;

		T get_value(){ return this->value; };
		void set_value(T value){ this->value = value; };

		bool get_valid(){ return this->valid; };
		bool set_valid(bool value){
			this->valid = value;
			if(this->valid) this->left->setForeground(Qt::green);
			else this->left->setForeground(Qt::red);

			return this->valid;
		};

		void set_icon(const QIcon& icon){ right->setIcon(icon); };
		QIcon get_icon(){ return right->icon(); };

		QStandardItem* right;

		private:
		bool valid;
		T value;
		QStandardItem* left;
	};

	// SIMPLE ITEM DEFINITION
	using SimpleItemWidget = QLineEdit;
	using SimpleItemType = QString;
	class SimpleItem: Item<SimpleItemWidget, SimpleItemType>{
		public:
		SimpleItem(ShipView* view, QStandardItem* ship,
		QString name, QMetaType::Type type): Item<SimpleItemWidget, SimpleItemType>(view, ship, name){
			this->type = type;
			this->check();
		};

		private:
		QMetaType::Type type;
		// TODO Fix check function
		virtual bool check() override{
			bool valid = false;
			switch(type){
				case(QMetaType::Float):
					valid = get_value().toFloat(&valid);
					break;
				case(QMetaType::Double):
					valid = get_value().toDouble(&valid);
					break;
				case(QMetaType::QString):
					valid = get_value().toFloat(&valid);
					break;
				case(QMetaType::Int):
					valid = get_value().toInt(&valid);
					break;
				// FIXME: Error handling here
				default:
					qDebug() << "Not prepared for this type";
					break;
			}
			return this->set_valid(valid);
		};
		virtual void init_widget(QWidget* editor) const override{
			SimpleItemWidget* widget = static_cast<SimpleItemWidget*>(editor);
			QObject::connect(this, &QStyledItemDelegate::commitData, widget, [this, widget](){
				SimpleItem* item = const_cast<SimpleItem*>(this);
				item->set_value(widget->text());
				item->check();
			});
		};
	};

	using ColorItemWidget = QColorDialog;
	using ColorItemType = QColor;
	class ColorItem: Item<ColorItemWidget, ColorItemType>{
		// Initialize; permanently assert this item as true
		public:
		ColorItem(ShipView* view, QStandardItem* ship, QString name):
		Item<ColorItemWidget, ColorItemType>(view, ship, name){
			// Choose random color, ensure validity
			auto rand_rgb = [](){ return randint(16) * 16; };
			QColor color;
			do{ color = QColor(rand_rgb(), rand_rgb(), rand_rgb()); }
			while(color.spec() == QColor::Invalid);

			IconEngine* icon_engine = new IconEngine(color);
			QIcon icon = icon_engine->get_icon();
			this->set_icon(icon);

			// This item will always be true
			this->check();
		};

		private:
		virtual bool check() override { return this->set_valid(true); };
		virtual void init_widget(QWidget* editor) const override{
			ColorItemWidget* widget = static_cast<ColorItemWidget*>(editor);
			QObject::connect(this, &QStyledItemDelegate::commitData, widget, [this, widget](){
				ColorItem* item = const_cast<ColorItem*>(this);

				IconEngine* icon_engine = new IconEngine(widget->selectedColor());
				item->set_icon(icon_engine->get_icon());
			});
		};
	};

	using PatternItemWidget = PatternSelect;
	using PatternItemType = Qt::BrushStyle;
	class PatternItem: Item<PatternItemWidget, PatternItemType>{
		public:
		PatternItem(ShipView* view, QStandardItem* ship, QString name):
		Item<PatternItemWidget, PatternItemType>(view, ship, name){
			// FIXME Fix immediately
			// Initialize widget in constructor
			//style_option.decorationAlignment(QFlags<Qt::AlignmentFlag>(Qt::AlignCenter));
			QStandardItemModel* model = static_cast<QStandardItemModel*>(view->model());
			QWidget* editor = this->createEditor(view->viewport(), QStyleOptionViewItem(), ship->index());
			view->setIndexWidget(model->indexFromItem(this->right), editor);

			// This item will always be true
			this->check();
		};
		private:
		virtual bool check() override { return this->set_valid(true); };
		virtual void init_widget(QWidget* editor) const override{
			//PatternItemType style = PATTERN_ARRAY[randint(PATTERN_ARRAY.size())].first;
			PatternItemWidget* widget = static_cast<PatternItemWidget*>(editor);
			PatternItem* item = const_cast<PatternItem*>(this);
		};
	};

	// TODO Create door class
	/*
	struct Door: Item{
		Door(QStandardItem* ship, QString name): Item(ship, name){};
	};
	*/

	struct Ship: public QStandardItem{
		Ship(ShipView* view): QStandardItem(){
			// Add this ship to the model of the view
			QStandardItemModel* model = static_cast<QStandardItemModel*>(view->model());
			model->insertRow(view->model()->rowCount(), static_cast<QStandardItem*>(this));

			// Add items and assign them their widgets as their delegate editor
			new SimpleItem(view, this, "Length", QMetaType::Float);
			new ColorItem(view, this, "Color");
			new PatternItem(view, this, "Pattern");
			new SimpleItem(view, this, "Width", QMetaType::Float);
		};
	};
};
