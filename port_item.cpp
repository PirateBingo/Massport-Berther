#include <QtCore>
#include <QtSvgWidgets>

const QString PORT_ID = "port.svg";
const QString BOLLARD_ID = "bollard.svg";
const QString WATER_TREE_ID = "water_tree.svg";
const QString OCEAN_ID = "ocean.svg";

auto get_svg_path = [](QString path){
	return QDir::currentPath() + "/geometry/" + path;
};

// Defined port items
// TODO Implement x and y
struct PortItem: public QGraphicsSvgItem{
	PortItem(QGraphicsScene* graphics_scene, QString path,
    [[maybe_unused]] float x, [[maybe_unused]] float y, int z = 0):
	QGraphicsSvgItem(path){
		// Configure item
		this->setFlags(QGraphicsItem::ItemIsMovable |
                       QGraphicsItem::ItemSendsGeometryChanges);
		this->setZValue(z);

		// Show item in graphics view
		graphics_scene->addItem(this);
		this->show();
	};

	// Overloaded method which renders the SVG 
    void paint(QPainter* painter,
	[[maybe_unused]] const QStyleOptionGraphicsItem* option,
    [[maybe_unused]] QWidget* widget) override{
		this->renderer()->render(painter, QRectF(0, 0, 3500, 1000));
    };
};

// Initialize graphics items based on the content of their respective SVG
struct Bollard: public PortItem{
	Bollard(QGraphicsScene* graphics_scene, float x, float y):
	PortItem(graphics_scene, get_svg_path(BOLLARD_ID), x, y){};
};

struct WaterTree: public PortItem{
	WaterTree(QGraphicsScene* graphics_scene, float x, float y):
	PortItem(graphics_scene, get_svg_path(WATER_TREE_ID), x, y){};
};

struct Port: public PortItem{
	Port(QGraphicsScene* graphics_scene):
	PortItem(graphics_scene, get_svg_path(PORT_ID), 0, 0){};
};

struct Ocean: public PortItem{
	Ocean(QGraphicsScene* graphics_scene):
	PortItem(graphics_scene, get_svg_path(OCEAN_ID), 0, 0){};
};
