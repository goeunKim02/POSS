# ui_styles.py
class ResultStyles:
    ACTIVE_BUTTON_STYLE = """
        QPushButton {
            background-color: #1428A0; 
            color: white; 
            font-weight: bold; 
            padding: 8px 8px; 
            border-radius: 4px;
        }
    """
    
    INACTIVE_BUTTON_STYLE = """
        QPushButton {
            background-color: #8E9CC9; 
            color: white; 
            font-weight: bold; 
            padding: 8px 8px; 
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #1428A0;
        }
    """
    
    EXPORT_BUTTON_STYLE = """
        QPushButton {
            background-color: #1428A0; 
            color: white; 
            font-weight: bold; 
            padding: 5px 15px; 
            border-radius: 5px; 
        }
        QPushButton:hover {
            background-color: #004C99;
        }
        QPushButton:pressed {
            background-color: #003366;
        }
    """
    
    MATERIAL_TABLE_STYLE = """
        QTableWidget {
            border: 1px solid #ffffff;
            gridline-color: #f0f0f0;
            background-color: white;
            border-radius: 0;
            margin-top: 0px;
            outline: none;
        }
        QHeaderView::section {
            background-color: #1428A0;
            color: white;
            padding: 4px;
            font-weight: bold;
            border: 1px solid #1428A0;
            border-radius: 0;
            outline: none;
        }
    """