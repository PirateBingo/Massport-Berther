#include <QtCore>
#include <QtWidgets>

#include "port_item.cpp"

const static constexpr float SCENE_WIDTH = 3500;
const static constexpr float SCENE_HEIGHT = 1000;

struct ShipMap: public QGraphicsView{
	ShipMap(QWidget* parent): QGraphicsView(parent){
		// Initialize graphics scene
		QGraphicsScene* scene = new QGraphicsScene(parent);
		this->setScene(scene);
		this->setSceneRect(QRectF(0, 0, SCENE_WIDTH, SCENE_HEIGHT));

		// Configure graphics view
		this->setCacheMode(QGraphicsView::CacheModeFlag::CacheBackground);
		this->setRenderHint(QPainter::RenderHint::Antialiasing);
		this->setTransformationAnchor(QGraphicsView::ViewportAnchor::AnchorUnderMouse);
		this->setResizeAnchor(QGraphicsView::ViewportAnchor::AnchorUnderMouse);
		this->scene()->setItemIndexMethod(QGraphicsScene::ItemIndexMethod::NoIndex);

		// TODO:
		// Draw background
		[[maybe_unused]] Port* port = new Port(this->scene());
		[[maybe_unused]] Ocean* ocean = new Ocean(this->scene());
	};
};
