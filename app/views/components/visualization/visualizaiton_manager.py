import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Basic visualization module that can be imported in different parts of the application
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

        if ax in None:
            fig, ax = plt.subplots(figsize=(8,5))

        # Convert data to frame needed for plotting
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
        

        # Create appropriate chart based on type
        if chart_type == 'bar':
            bars = ax.bar(x_data, y_data, color=kwargs.get('color', 'steelblue'), 
                          alpha=kwargs.get('alpha', 0.8), width=kwargs.get('width', 0.7))
            
            # Add value Labels if requested
            if kwargs.get('show_value', True):
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{heigth:.1f}' if isinstance(height, float) else f'{height}',
                            ha='center', va='bottom', fontsize=kwargs.get('value_fontsize', 9))
                    
        elif chart_type == 'line':
            lines = ax.plot(x_data, y_data, marker=kwargs.get('marker', 'o'), 
                    linestyle=kwargs.get('linestyle', '-'),
                    linewidth=kwargs.get('linewidth', 2),
                    color=kwargs.get('color', 'steelblue'),
                    markersize=kwargs.get('markersize', 5))
                
            # Add value labels if requested
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
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as circle

            # Customize text properties
            if autotexts and kwargs.get('show_pct', True):
                for autotext in autotexts:
                    autotext.set_fontsize(kwargs.get('pct_fontsize', 9))
                    autotext.set_color(kwargs.get('pct_color', 'white'))

        elif chart_type == 'heatmap':
            if isinstance(data, pd.DataFrame):
                im = ax.imshow(data.values, cmap=kwargs.get('cmap', 'viridis'))

                # Show all ticks and label theme
                ax.set_xticks(np.arange(len(data.columns)))
                ax.set_yticks(np.arange(len(data.index)))
                ax.set_xticklabels(data.columns)
                ax.set_yticklabels(data.index)

                # Rotata the tick labels and set alignmet
                plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

                # Add colorbar
                if kwargs.get('show_colorbar', True):
                    plt.colorbar(im, ax=ax)

                # Add text annotations if requested
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
            scatter = ax.scatter(x_data, y_data, 
                                 c=kwargs.get('color', 'steelblue'), 
                                 s=kwargs.get('size', 50), 
                                 alpha=kwargs.get('alpha', 0.7), 
                                 marker=kwargs.get('marker', 'o'))
            
            # Add best fit line if requested
            if kwargs.get('show_trendline', False) and len(x_data) > 1:
                try:
                    z = np.ployfit(x_data, y_data, 1)
                    p = np.ploy1d(z)
                    ax.plot(x_data, p(x_data), '--', color=kwargs.get('trendline_color', 'red'))
                except:
                    pass # Skip trendline if there's an error (e.g., non-numeric data)
            
        else:
            raise ValueError(f"Unspported chart type: {chart_type}")
        
        # Add labels and title
        ax.set_title(title, fontsize=kwargs.get('title_fontsize', 14))
        ax.set_xlabel(xlabel, fontsize=kwargs.get('label_fontsize', 12))
        ax.set_ylabel(ylabel, fontsize=kwargs.get('label_fontsize', 12))

        # Add grid if requested
        if kwargs.get('show_grid', True):
            ax.grid(alpha=kwargs.get('grid_alpha', 0.3), linestyle=kwargs.get('grid_style', '--'))

        # Rotate x labels if requested or if they seem long
        if kwargs.get('rotate_xlabels', False) or (len(x_data) > 0 and any(len(str(x)) > 5 for x in x_data)):
            plt.setp(ax.get_xticklabels(), rotation=kwargs.get('xlabels_rotation', 45), 
                ha=kwargs.get('xlabels_ha', 'right'))
        
        # Customize y-axis limits if provided
        if 'ylim' in kwargs:
            ax.set_ylim(kwargs['ylim'])

        # Set figure tight layout
        if ax.figure:
            ax.figure.tight_layout()

        return ax
    

    # 가동률
    @staticmethod
    def create_utilization_chart(data, by='day', ax=None, **kwargs):
        """
        Create utilization rate chart by day or line

        Args:
            data: Dictionary with days/lines as keys and utilization rates as values
            by: 'day' or 'line'
            ax: Matplotlib axes to plot on (optional)
            **kwargs: Additional parameters for chart customization
        """
        title = f"Utilization Rate by {'Day' if by == 'day' else 'Production Line'}"
        xlabel = 'Day' if by == 'day' else 'Production Line'
        return VisualizationManager.create_chart(
            data, 
            chart_type='bar', 
            title=title, 
            xlabel=xlabel, 
            ylabel='Utilization Rate (%)',
            ax=ax,
            ylim=(0, 100),
            **kwargs
        )
   
    @staticmethod
    def create_production_chart(data, by='day', chart_type='bar', ax=None, **kwargs):
        """
        Create production chart by day or line

        Args:
            data: Dictionary with days/lines as keys and production quantities as values
            by: 'day' or 'line'
            chart_type: 'bar' or 'line'
            ax: Matplotlib axes to plot on (optional)
            **kwargs: Additional parameters for chart customization
        """
        title = f"Production by {'Day' if by == 'day' else 'Production Line'}"
        xlabel = 'Day' if by == 'day' else 'Production Line'
        return VisualizationManager.create_chart(
            data, 
            chart_type=chart_type, 
            title=title, 
            xlabel=xlabel, 
            ylabel='Production (units)',
            ax=ax,
            **kwargs
        )
   
    @staticmethod
    def create_defect_rate_chart(data, by='product', ax=None, **kwargs):
        """
        Create defect rate chart by product or line

        Args:
            data: Dictionary with products/lines as keys and defect rates as values
            by: 'product' or 'line'
            ax: Matplotlib axes to plot on (optional)
            **kwargs: Additional parameters for chart customization
        """
        title = f"Defect Rate by {'Product' if by == 'product' else 'Production Line'}"
        xlabel = 'Product' if by == 'product' else 'Production Line'
        return VisualizationManager.create_chart(
            data, 
            chart_type='bar', 
            title=title, 
            xlabel=xlabel, 
            ylabel='Defect Rate (%)',
            ax=ax,
            **kwargs
        )
   
    @staticmethod
    def create_shift_comparison_chart(data, metric='production', ax=None, **kwargs):
        """
        Create shift comparison chart (day vs night shift)

        Args:
            data: Dictionary with format {'Day Shift': {day1: value1, day2: value2...}, 
                                        'Night Shift': {day1: value1, day2: value2...}}
            metric: What's being compared ('production', 'efficiency', etc.)
            ax: Matplotlib axes to plot on (optional)
            **kwargs: Additional parameters for chart customization
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))

        # Extract data
        days = list(data['Day Shift'].keys())
        day_values = list(data['Day Shift'].values())
        night_values = list(data['Night Shift'].values())

        # Set width of bars
        barWidth = 0.35

        # Set position of bars on X axis
        r1 = np.arange(len(days))
        r2 = [x + barWidth for x in r1]

        # Create bars
        bars1 = ax.bar(r1, day_values, width=barWidth, label='Day Shift', color='skyblue')
        bars2 = ax.bar(r2, night_values, width=barWidth, label='Night Shift', color='navy')

        # Add values on bars
        if kwargs.get('show_values', True):
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}' if isinstance(height, float) else f'{height}',
                            ha='center', va='bottom', fontsize=kwargs.get('value_fontsize', 9))

        # Add labels and title
        metric_title = metric.capitalize()
        ax.set_title(f'Day vs Night Shift {metric_title} Comparison', fontsize=kwargs.get('title_fontsize', 14))
        ax.set_xlabel('Day of Week', fontsize=kwargs.get('label_fontsize', 12))
        ax.set_ylabel(metric_title, fontsize=kwargs.get('label_fontsize', 12))

        # Add xticks on the middle of the group bars
        ax.set_xticks([r + barWidth/2 for r in range(len(days))])
        ax.set_xticklabels(days)

        # Create legend
        ax.legend()

        # Add grid
        if kwargs.get('show_grid', True):
            ax.grid(alpha=kwargs.get('grid_alpha', 0.3), linestyle=kwargs.get('grid_style', '--'), axis='y')

        # Set figure tight layout
        if ax.figure:
            ax.figure.tight_layout()
            
        return ax
   
    @staticmethod
    def create_time_series_chart(data, metric='production', ax=None, **kwargs):
        """
        Create time series chart
        
        Args:
            data: Dictionary with dates as keys and values for the metric
            metric: What's being tracked over time
            ax: Matplotlib axes to plot on (optional)
            **kwargs: Additional parameters for chart customization
        """
        return VisualizationManager.create_chart(
            data, 
            chart_type='line', 
            title=f'{metric.capitalize()} Over Time', 
            xlabel='Date', 
            ylabel=metric.capitalize(),
            ax=ax,
            marker=kwargs.get('marker', 'o'),
            **kwargs
        )
   
    @staticmethod
    def create_product_distribution_chart(data, ax=None, **kwargs):
        """
        Create product distribution pie chart
        
        Args:
            data: Dictionary with products as keys and production quantities as values
            ax: Matplotlib axes to plot on (optional)
            **kwargs: Additional parameters for chart customization
        """
        return VisualizationManager.create_chart(
            data, 
            chart_type='pie', 
            title='Product Distribution', 
            ax=ax,
            **kwargs
        )
   
    @staticmethod
    def create_heatmap_chart(data, title='Heatmap', ax=None, **kwargs):
        """
        Create heatmap chart
        
        Args:
            data: DataFrame with data for heatmap
            title: Chart title
            ax: Matplotlib axes to plot on (optional)
            **kwargs: Additional parameters for chart customization
        """
        return VisualizationManager.create_chart(
            data, 
            chart_type='heatmap', 
            title=title, 
            ax=ax,
            **kwargs
        )