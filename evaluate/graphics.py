import matplotlib.pyplot as plt
import seaborn as sns

import config.config as config


def transform_format_data(data):
    global_data = []
    individual_data = []

    for entity, details in data.items():
        global_record = {
            'entity': entity,
            'avg_score': float(details['avg_score']) if details['avg_score'] is not None else 0.0,
            'best_score': float(details['best_score']) if details['best_score'] is not None else 0.0,
            'worst_score': float(details['worst_score']) if details['worst_score'] is not None else 0.0,
            'avg_rank': float(details['avg_rank']) if details['avg_rank'] is not None else 0.0,
            'best_rank': int(details['best_rank']) if details['best_rank'] is not None else 0,
            'worst_rank': int(details['worst_rank']) if details['worst_rank'] is not None else 0,
            'avg_diff_with_best_score': float(details['avg_diff_with_best_score']) if details['avg_diff_with_best_score'] is not None else 0.0,
            'min_diff_with_best_score': float(details['min_diff_with_best_score']) if details['min_diff_with_best_score'] is not None else 0.0,
            'max_diff_with_best_score': float(details['max_diff_with_best_score']) if details['max_diff_with_best_score'] is not None else 0.0,
        }
        global_data.append(global_record)
    
        for key, value in details.items():
            if key.endswith('.jpeg'):
                individual_record = {
                    'entity': entity,
                    'score': float(value['score']) if value['score'] is not None else 0.0,
                    'rank': int(value['rank']) if value['rank'] is not None else 0
                }
                individual_data.append(individual_record)
    
    return global_data, individual_data

    
def make_bar_plot_avg_scores(global_df):
    # Define a color palette with 5 colors
    palette = sns.color_palette("husl", 5)

    # Bar plot for average scores
    plt.figure(figsize=(15, 8))
    ax = sns.barplot(x='entity', y='avg_score', data=global_df, palette=palette)
    plt.title('Average Score Percentage by Entity')
    plt.xlabel('Entity')
    plt.ylabel('Average Score (%)')
    plt.xticks(rotation=90)

    # Get current y-axis limits
    ymin, ymax = plt.gca().get_ylim()

    # Adding dashed lines every 10% within the current y-axis limits
    for y in range(int(ymin), int(ymax)+1, 10):
        plt.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)
    
    # Customize tick labels with the corresponding colors
    for tick_label, color in zip(ax.get_xticklabels(), [palette[i % len(palette)] for i in range(len(global_df['entity'].unique()))]):
        tick_label.set_color(color)
    
    # Save the image
    plt.savefig('docs/models_performances/evaluations/average_score_barplot.png', bbox_inches='tight')
    plt.show()

def make_bar_plot_avg_difference_best_scores(global_df):
    # Define a color palette with 5 colors
    palette = sns.color_palette("husl", 5)
    
    # Bar plot for average difference with best scores
    plt.figure(figsize=(15, 8))
    ax = sns.barplot(x='entity', y='avg_diff_with_best_score', data=global_df, palette=palette)
    plt.title('Average Difference with Best Scores by Entity')
    plt.xlabel('Entity')
    plt.ylabel('Average Difference with Best Scores (%)')
    plt.xticks(rotation=90)

    # Get current y-axis limits
    ymin, ymax = plt.gca().get_ylim()

    # Adding dashed lines every 10% within the current y-axis limits
    for y in range(int(ymin), int(ymax)+1, 10):
        plt.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)

    # Customize tick labels with the corresponding colors
    for tick_label, color in zip(ax.get_xticklabels(), [palette[i % len(palette)] for i in range(len(global_df['entity'].unique()))]):
        tick_label.set_color(color)
    
    # Save the image
    plt.savefig('docs/models_performances/evaluations/avg_difference_with_best_scores_barplot.png', bbox_inches='tight')
    plt.show()

def make_box_plot_avg_score_percentage(individual_df):
    # Define a color palette with 5 colors
    palette = sns.color_palette("husl", 5)
    
    # Box plot for score percentages
    plt.figure(figsize=(15, 8))
    ax = sns.boxplot(x='entity', y='score', data=individual_df, palette=palette)
    plt.title('Score Percentage Distribution by Entity')
    plt.xlabel('Entity')
    plt.ylabel('Scores (%)')
    plt.xticks(rotation=90)

    # Customize tick labels with the corresponding colors
    for tick_label, color in zip(ax.get_xticklabels(), [palette[i % len(palette)] for i in range(len(individual_df['entity'].unique()))]):
        tick_label.set_color(color)
    
    # Save the image
    plt.savefig('docs/models_performances/evaluations/score_distribution_boxplot.png', bbox_inches='tight')
    plt.show()
    
    
def make_box_plot_avg_rankings(individual_df):
    # Define a color palette with 5 colors
    palette = sns.color_palette("husl", 5)
    
    # Box plot for rankings
    plt.figure(figsize=(15, 8))
    ax = sns.boxplot(x='entity', y='rank', data=individual_df, palette=palette)
    plt.title('Ranking Distribution by Entity')
    plt.xlabel('Entity')
    plt.ylabel(f'Rankings (/{config.NUM_ENTITIES})')
    plt.xticks(rotation=90)

    # Invert the y-axis
    # plt.gca().invert_yaxis()

    # Customize tick labels with the corresponding colors
    for tick_label, color in zip(ax.get_xticklabels(), [palette[i % len(palette)] for i in range(len(individual_df['entity'].unique()))]):
        tick_label.set_color(color)

    # Save the image
    plt.savefig('docs/models_performances/evaluations/rank_distribution_boxplot.png', bbox_inches='tight')
    plt.show()