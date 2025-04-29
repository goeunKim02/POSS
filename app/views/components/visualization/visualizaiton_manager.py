import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Basic visualization module
class VisualizationManager:
    @staticmethod
    def create_chart(data, chart_type='bar', title='Chart', xlabel='X', ylabel='Y', ax=None, **kwargs):
        """
        Generic chart creation method

        Args:
        data: Dictionary or DataFrame with data to visualize
        chart_type: Type of chart ('bar', 'line', 'pie', 'heatmap', etc)
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        ax: Matplotlib axes to plot on (optional)
        **kwargs: Additional parameters for specific chart types

        Returns:
        Matplotlib axes with the plot
        """

        if ax is None:
            fig, ax = plt.subplots(figsize=(8,5))

        # 시각화에 필요한 형식으로 데이터 변환
        if isinstance(data, dict):
            x_data = list(data.keys())
            y_data = list(data.values())
        elif isinstance(data, pd.DataFrame):
            if 'x' in kwargs and 'y' in kwargs:
                x_data = data[kwargs['x']].tolist()
                y_data = data[kwargs['y']].tolist()
            else:
                x_data = data.index.tolist()
                y_data = data.loc[:, 0].tolist() if data.shape[1] > 0 else []
        else:
            raise ValueError("Data must be a dictionary or DataFrame")
        

        # 유형에 따라 차트 생성
        if chart_type == 'bar':
            bars = ax.bar(x_data, y_data, color=kwargs.get('color', 'steelblue'), 
                          alpha=kwargs.get('alpha', 0.8), width=kwargs.get('width', 0.7))
            
            # 필요시 값 레이블 추가
            if kwargs.get('show_value', True):
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}' if isinstance(height, float) else f'{height}',
                            ha='center', va='bottom', fontsize=kwargs.get('value_fontsize', 9))
                    
        elif chart_type == 'line':
            ax.plot(x_data, y_data, marker=kwargs.get('marker', 'o'), 
                linestyle=kwargs.get('linestyle', '-'),
                linewidth=kwargs.get('linewidth', 2),
                color=kwargs.get('color', 'steelblue'),
                markersize=kwargs.get('markersize', 5))
                
            # 필요시 값 레이블 추가
            if kwargs.get('show_values', True):
                for i, value in enumerate(y_data):
                    ax.text(i, value, f'{value:.1f}' if isinstance(value, float) else f'{value}',
                            ha='center', va='bottom', fontsize=kwargs.get('value_fontsize', 9))
                    
        elif chart_type == 'pie':
            wedges, texts, autotexts = ax.pie(
                y_data,
                labels=None if kwargs.get('hide_labels', False) else x_data,
                autopct='%1.1f%%' if kwargs.get('show_pct', True) else None,
                startangle=kwargs.get('startangle', 90),
                colors=kwargs.get('colors', None)
            )
            ax.axis('equal')  # 원형 차트가 원으로 그려지도록 동일한 비율 설정

            # 텍스트 속성 사용자 정의
            if autotexts and kwargs.get('show_pct', True):
                for autotext in autotexts:
                    autotext.set_fontsize(kwargs.get('pct_fontsize', 9))
                    autotext.set_color(kwargs.get('pct_color', 'white'))

        elif chart_type == 'heatmap':
            if isinstance(data, pd.DataFrame):
                im = ax.imshow(data.values, cmap=kwargs.get('cmap', 'viridis'))

                # 모든 눈금 표시 및 레이블 지정
                ax.set_xticks(np.arange(len(data.columns)))
                ax.set_yticks(np.arange(len(data.index)))
                ax.set_xticklabels(data.columns)
                ax.set_yticklabels(data.index)

                # 눈금 레이블 회전 및 정렬 설정
                plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

                # 색상 막대 추가
                if kwargs.get('show_colorbar', True):
                    plt.colorbar(im, ax=ax)

                # 필요시 텍스트 주석 추가
                if kwargs.get('show_values', True):
                    for i in range(len(data.index)):
                        for j in range(len(data.columns)):
                            value = data.iloc[i, j]
                            text_color = 'white' if value > (data.values.max() + data.values.min()) / 2 else 'black'
                            ax.text(j, i, f'{value:.1f}' if isinstance(value, float) else f'{value}', 
                                    ha="center", va="center", color=text_color, fontsize=kwargs.get('value_fontsize', 9))
                            
            else:
                raise ValueError("Data must be a DataFrame for heatmap visualization")
            
        elif chart_type == 'scatter':
            ax.scatter(x_data, y_data, 
                        c=kwargs.get('color', 'steelblue'), 
                        s=kwargs.get('size', 50), 
                        alpha=kwargs.get('alpha', 0.7), 
                        marker=kwargs.get('marker', 'o'))
            
            # 필요시 추세선 추가
            if kwargs.get('show_trendline', False) and len(x_data) > 1:
                try:
                    z = np.polyfit(x_data, y_data, 1)
                    p = np.poly1d(z)
                    ax.plot(x_data, p(x_data), '--', color=kwargs.get('trendline_color', 'red'))
                except:
                    pass # 오류 발생 시 추세선 생략 (예: 비수치 데이터)
            
        else:
            raise ValueError(f"Unspported chart type: {chart_type}")
        
        # 레이블 및 제목 추가
        ax.set_title(title, fontsize=kwargs.get('title_fontsize', 20))
        ax.set_xlabel(xlabel, fontsize=kwargs.get('label_fontsize', 18))
        ax.set_ylabel(ylabel, fontsize=kwargs.get('label_fontsize', 18))

        # 여기에 tick label 폰트 크기 설정 코드 추가
        tick_fontsize = kwargs.get('tick_fontsize', 16)  
        ax.tick_params(axis='both', which='major', labelsize=tick_fontsize)

        # 필요시 그리드 추가
        if kwargs.get('show_grid', True):
            ax.grid(alpha=kwargs.get('grid_alpha', 0.3), linestyle=kwargs.get('grid_style', '--'))

        # 필요한 경우 X축 레이블 회전 (레이블이 길거나 요청된 경우)
        if kwargs.get('rotate_xlabels', False) or (len(x_data) > 0 and any(len(str(x)) > 5 for x in x_data)):
            plt.setp(ax.get_xticklabels(), rotation=kwargs.get('xlabels_rotation', 45), 
                ha=kwargs.get('xlabels_ha', 'right'))
        
        # Y축 범위 사용자 정의 (제공된 경우)
        if 'ylim' in kwargs:
            ax.set_ylim(kwargs['ylim'])

        # 그림 레이아웃 조정
        if ax.figure:
            ax.figure.tight_layout()

        return ax
    
