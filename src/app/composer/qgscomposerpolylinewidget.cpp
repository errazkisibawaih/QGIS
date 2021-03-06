/***************************************************************************
                         qgscomposerpolylinewidget.cpp
    begin                : March 2016
    copyright            : (C) 2016 Paul Blottiere, Oslandia
    email                : paul dot blottiere at oslandia dot com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

#include "qgscomposerpolylinewidget.h"
#include "qgscomposerpolyline.h"
#include "qgscomposeritemwidget.h"
#include "qgssymbolselectordialog.h"
#include "qgsstyle.h"
#include "qgssymbollayerutils.h"

QgsComposerPolylineWidget::QgsComposerPolylineWidget( QgsComposerPolyline* composerPolyline ):
    QgsComposerItemBaseWidget( nullptr, composerPolyline )
    , mComposerPolyline( composerPolyline )
{
  setupUi( this );

  //add widget for general composer item properties
  QgsComposerItemWidget* itemPropertiesWidget = new QgsComposerItemWidget( this, composerPolyline );

  itemPropertiesWidget->showBackgroundGroup( false );
  itemPropertiesWidget->showFrameGroup( false );
  mainLayout->addWidget( itemPropertiesWidget );

  // update style icon
  updatePolylineStyle();

  if ( mComposerPolyline )
    connect( mComposerPolyline, SIGNAL( itemChanged() ), this, SLOT( setGuiElementValues() ) );
}

QgsComposerPolylineWidget::~QgsComposerPolylineWidget()
{
}

void QgsComposerPolylineWidget::on_mLineStyleButton_clicked()
{
  if ( !mComposerPolyline )
    return;

  QScopedPointer<QgsLineSymbol> newSymbol;
  newSymbol.reset( mComposerPolyline->polylineStyleSymbol()->clone() );

  QgsExpressionContext context = mComposerPolyline->createExpressionContext();
  QgsSymbolSelectorDialog d( newSymbol.data(), QgsStyle::defaultStyle(),
                             nullptr, this );
  QgsSymbolWidgetContext symbolContext;
  symbolContext.setExpressionContext( &context );
  d.setContext( symbolContext );

  if ( d.exec() == QDialog::Accepted )
  {
    mComposerPolyline->beginCommand( tr( "Polyline style changed" ) );
    mComposerPolyline->setPolylineStyleSymbol( newSymbol.data() );
    updatePolylineStyle();
    mComposerPolyline->endCommand();
  }
}

void QgsComposerPolylineWidget::setGuiElementValues()
{
  if ( !mComposerPolyline )
    return;

  updatePolylineStyle();
}

void QgsComposerPolylineWidget::updatePolylineStyle()
{
  if ( mComposerPolyline )
  {
    QIcon icon = QgsSymbolLayerUtils::symbolPreviewIcon( mComposerPolyline->polylineStyleSymbol(), mLineStyleButton->iconSize() );
    mLineStyleButton->setIcon( icon );
  }
}
