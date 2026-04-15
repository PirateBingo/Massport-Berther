#include <QtCore>

#pragma once

const constexpr Qt::ItemFlags LABEL_FLAGS = Qt::ItemIsEnabled;
const constexpr Qt::ItemFlags LABEL_SELECTABLE_FLAGS = Qt::ItemIsEnabled |
                                                       Qt::ItemIsSelectable;
const constexpr Qt::ItemFlags ENTRY_FLAGS = Qt::ItemIsEnabled |
                                            Qt::ItemIsSelectable |
                                            Qt::ItemIsEditable;

const constexpr Qt::ItemFlags SHIP_INVALID_FLAGS = Qt::ItemIsEnabled;
const constexpr Qt::ItemFlags SHIP_VALID_FLAGS = Qt::ItemIsEnabled |
                                                 Qt::ItemIsSelectable |
                                                 Qt::ItemIsEditable |
                                                 Qt::ItemIsDragEnabled |
                                                 Qt::ItemIsDropEnabled;

enum class Side {port,      // Left Side
                 starboard, // Right Side
                 both};

using brush_pattern = std::pair<Qt::BrushStyle, QString>;
const std::array<brush_pattern, 14> PATTERN_ARRAY {
	brush_pattern{Qt::SolidPattern, "Solid Pattern"},
	brush_pattern{Qt::Dense1Pattern, "Dense Pattern 1"},
	brush_pattern{Qt::Dense2Pattern, "Dense Pattern 2"},
	brush_pattern{Qt::Dense3Pattern, "Dense Pattern 3"},
	brush_pattern{Qt::Dense4Pattern, "Dense Pattern 4"},
	brush_pattern{Qt::Dense5Pattern, "Dense Pattern 5"},
	brush_pattern{Qt::Dense6Pattern, "Dense Pattern 6"},
	brush_pattern{Qt::Dense7Pattern, "Dense Pattern 7"},
	brush_pattern{Qt::HorPattern, "Horizontal Pattern"},
	brush_pattern{Qt::VerPattern, "Vertical Pattern"},
	brush_pattern{Qt::CrossPattern, "Cross Pattern"},
	brush_pattern{Qt::BDiagPattern, "Backwards Diagonal Pattern"},
	brush_pattern{Qt::FDiagPattern, "Forwards Diagonal Pattern"},
	brush_pattern{Qt::DiagCrossPattern, "Diagonal Cross Pattern"}
};
