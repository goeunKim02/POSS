class ItemStyle:
    # 기본 스타일 
    DEFAULT_STYLE = """
        QFrame {
            background-color: #F8F9FA;
            border: 1px solid #DEE2E6;
            border-radius: 4px;
            padding: 5px 5px 5px 15px;  
            margin: 2px;
        }
        QLabel {
            font-weight: normal;
        }
    """

    # 선택됐을 때 스타일 
    SELECTED_STYLE = """
        QFrame {
            background-color: #E3F2FD;
            border: 2px solid #1976D2;
            border-radius: 4px;
            padding: 5x 5px 5px 15px;  
            margin: 2px;
        }
        QLabel {
            font-weight: bold;
        }
    """

    # 호버 스타일 
    HOVER_STYLE = """
        QFrame {
            background-color: #E3F2FD;
            border: 1px solid #1976D2;
            border-radius: 4px;
            padding: 5px 5x 5px 15px;
            margin: 2px;
        }
        QLabel {
        }
    """

    # 각 상태별 스타일들 - 모두 같은 패딩으로 통일
    # 자재 부족 스타일
    SHORTAGE_STYLE = DEFAULT_STYLE
    SHORTAGE_SELECTED_STYLE = SELECTED_STYLE
    SHORTAGE_HOVER_STYLE = HOVER_STYLE

    # 사전할당 스타일
    PRE_ASSIGNED_STYLE = DEFAULT_STYLE
    PRE_ASSIGNED_SELECTED_STYLE = SELECTED_STYLE
    PRE_ASSIGNED_HOVER_STYLE = HOVER_STYLE

    # 출하 실패 스타일
    SHIPMENT_FAILURE_STYLE = DEFAULT_STYLE
    SHIPMENT_FAILURE_SELECTED_STYLE = SELECTED_STYLE
    SHIPMENT_FAILURE_HOVER_STYLE = HOVER_STYLE

    # 복합 상태들도 모두 같은 스타일 사용
    PRE_ASSIGNED_SHORTAGE_STYLE = DEFAULT_STYLE
    PRE_ASSIGNED_SHORTAGE_SELECTED_STYLE = SELECTED_STYLE
    PRE_ASSIGNED_SHORTAGE_HOVER_STYLE = HOVER_STYLE

    PRE_ASSIGNED_SHIPMENT_STYLE = DEFAULT_STYLE
    PRE_ASSIGNED_SHIPMENT_SELECTED_STYLE = SELECTED_STYLE
    PRE_ASSIGNED_SHIPMENT_HOVER_STYLE = HOVER_STYLE

    SHORTAGE_SHIPMENT_STYLE = DEFAULT_STYLE
    SHORTAGE_SHIPMENT_SELECTED_STYLE = SELECTED_STYLE
    SHORTAGE_SHIPMENT_HOVER_STYLE = HOVER_STYLE

    PRE_ASSIGNED_SHORTAGE_SHIPMENT_STYLE = DEFAULT_STYLE
    PRE_ASSIGNED_SHORTAGE_SHIPMENT_SELECTED_STYLE = SELECTED_STYLE
    PRE_ASSIGNED_SHORTAGE_SHIPMENT_HOVER_STYLE = HOVER_STYLE