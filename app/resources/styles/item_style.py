class ItemStyle:
    # 기본 스타일 정의
    DEFAULT_STYLE = """
        background-color: #F0F0F0;
        border: 1px solid #D0D0D0;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """

    # 선택됐을 때 스타일 정의
    SELECTED_STYLE = """
        background-color: #C2E0FF;
        border: 1px solid #0078D7;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """

    # 호버 스타일 정의
    HOVER_STYLE = """
        background-color: #E6E6E6;
        border: 1px solid #B8B8B8;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """

    # 자재 부족 스타일 추가
    SHORTAGE_STYLE = """
        background-color: #FFE0E0;
        border: 1px solid #FF8080;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """
    
    SHORTAGE_SELECTED_STYLE = """
        background-color: #FFC0C0;
        border: 1px solid #0078D7;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """
    
    SHORTAGE_HOVER_STYLE = """
        background-color: #FFC8C8;
        border: 1px solid #FF6060;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """

    # 사전할당 스타일
    PRE_ASSIGNED_STYLE = """
        background-color: #F0F0F0;
        border: 3px solid #000000;
        border-radius: 4px;
        padding: 3px;
        margin: 2px;
    """

    PRE_ASSIGNED_SELECTED_STYLE = """
        background-color: #C2E0FF;
        border: 3px solid #0078D7;
        border-radius: 4px;
        padding: 3px;
        margin: 2px;
    """
    
    PRE_ASSIGNED_HOVER_STYLE = """
        background-color: #E6E6E6;
        border: 3px solid #4CAF50;
        border-radius: 4px;
        padding: 3px;
        margin: 2px;
    """

    # 출하 실패 스타일
    SHIPMENT_FAILURE_STYLE = """
        background-color: #fcf9c0;
        border: 1px solid #FFCCCC;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """
    
    SHIPMENT_FAILURE_SELECTED_STYLE = """
        background-color: #FFCCCC;
        border: 1px solid #fcf67e;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """
    
    SHIPMENT_FAILURE_HOVER_STYLE = """
        background-color: #faf8ca;
        border: 1px solid #faf24d;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """

    # 복합 상태 스타일들 
    # 사전할당 + 자재부족 (자재부족 배경 + 굵은 테두리)
    PRE_ASSIGNED_SHORTAGE_STYLE = """
        background-color: #FFE0E0;
        border: 4px solid #000000;
        border-radius: 4px;
        padding: 3px;
        margin: 2px;
    """

    PRE_ASSIGNED_SHORTAGE_SELECTED_STYLE = """
        background-color: #FFC0C0;
        border: 4px solid #0078D7;
        border-radius: 4px;
        padding: 3px;
        margin: 2px;
    """

    PRE_ASSIGNED_SHORTAGE_HOVER_STYLE = """
        background-color: #FFC8C8;
        border: 4px solid #FF6060;
        border-radius: 4px;
        padding: 3px;
        margin: 2px;
    """

    # 사전할당 + 출하실패 (출하실패 배경 + 굵은 테두리)
    PRE_ASSIGNED_SHIPMENT_STYLE = """
        background-color: #fcf9c0;
        border: 4px solid #000000;
        border-radius: 4px;
        padding: 3px;
        margin: 2px;
    """

    PRE_ASSIGNED_SHIPMENT_SELECTED_STYLE = """
        background-color: #faf593;
        border: 4px solid #fcf67e;
        border-radius: 4px;
        padding: 3px;
        margin: 2px;
    """

    PRE_ASSIGNED_SHIPMENT_HOVER_STYLE = """
        background-color: #faf8ca;
        border: 4px solid #faf24d;
        border-radius: 4px;
        padding: 3px;
        margin: 2px;
    """

        # 자재부족 + 출하실패 (자재부족 배경 우선)
    SHORTAGE_SHIPMENT_STYLE = """
        background-color: #FFE0E0;
        border: 1px solid #FF8080;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """

    SHORTAGE_SHIPMENT_SELECTED_STYLE = """
        background-color: #FFC0C0;
        border: 1px solid #0078D7;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """

    SHORTAGE_SHIPMENT_HOVER_STYLE = """
        background-color: #FFC8C8;
        border: 1px solid #FF6060;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """

    # 모든 상태 조합 (사전할당 + 자재부족 + 출하실패)
    PRE_ASSIGNED_SHORTAGE_SHIPMENT_STYLE = """
        background-color: #FFE0E0;
        border: 3px solid #000000;
        border-radius: 4px;
        padding: 3px;
        margin: 2px;
    """

    PRE_ASSIGNED_SHORTAGE_SHIPMENT_SELECTED_STYLE = """
        background-color: #FFC0C0;
        border: 3px solid #0078D7;
        border-radius: 4px;
        padding: 3px;
        margin: 2px;
    """

    PRE_ASSIGNED_SHORTAGE_SHIPMENT_HOVER_STYLE = """
        background-color: #FFC8C8;
        border: 3px solid #FF6060;
        border-radius: 4px;
        padding: 3px;
        margin: 2px;
    """

    # 검증 에러 상태 스타일
    VALIDATION_ERROR_STYLE = """
        background-color: #FFEBEE;
        border: 2px solid #F44336;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """

    VALIDATION_ERROR_SELECTED_STYLE = """
        background-color: #FFCDD2;
        border: 2px solid #0078D7;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """
    
    VALIDATION_ERROR_HOVER_STYLE = """
        background-color: #FFD7DA;
        border: 2px solid #DC2626;
        border-radius: 4px;
        padding: 5px;
        margin: 2px;
    """