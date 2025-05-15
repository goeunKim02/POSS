class ItemStyle:
    # 기본 스타일 정의 - 선은 paintEvent에서 그리므로 기본적인 스타일만
    DEFAULT_STYLE = """
        QLabel {
            background-color: #F8F9FA;
            border: 1px solid #DEE2E6;
            border-radius: 4px;
            padding: 5px 5px 5px 15px;  /* 왼쪽 패딩을 늘려서 선이 그려질 공간 확보 */
            margin: 2px;
            font-weight: normal;
        }
    """

    # 선택됐을 때 스타일 정의
    SELECTED_STYLE = """
        QLabel {
            background-color: #E3F2FD;
            border: 2px solid #1976D2;
            border-radius: 4px;
            padding: 4px 4px 4px 14px;  /* 선택 시 border가 두꺼워지므로 패딩 조정 */
            margin: 2px;
            font-weight: bold;
        }
    """

    # 호버 스타일 정의
    HOVER_STYLE = """
        QLabel {
            background-color: #F5F5F5;
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            padding: 5px 5px 5px 15px;
            margin: 2px;
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