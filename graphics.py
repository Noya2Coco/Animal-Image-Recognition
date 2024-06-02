import matplotlib.pyplot as plt
import seaborn as sns


def transform_format_data(data):
    global_data = []
    individual_data = []

    for entity, details in data.items():
        global_record = {
            'animal': entity,
            'average_scores_percentage': float(details['average_scores_percentage'].strip('%')) if details['average_scores_percentage'] is not None else 0.0,
            'best_score_percentage': float(details['best_score_percentage'].strip('%')) if details['best_score_percentage'] is not None else 0.0,
            'worst_score_percentage': float(details['worst_score_percentage'].strip('%')) if details['worst_score_percentage'] is not None else 0.0,
            'average_rankings': float(details['average_rankings'].split('/')[0]) if details['average_rankings'] is not None else 0.0,
            'best_ranking': int(details['best_ranking'].split('/')[0]) if details['best_ranking'] is not None else 0,
            'worst_ranking': int(details['worst_ranking'].split('/')[0]) if details['worst_ranking'] is not None else 0,
            'average_difference_with_best_scores': float(details['average_difference_with_best_scores'].strip('%+')) if details['average_difference_with_best_scores'] is not None else 0.0,
            'min_difference_with_best_scores': float(details['min_difference_with_best_scores'].strip('%+')) if details['min_difference_with_best_scores'] is not None else 0.0,
            'max_difference_with_best_scores': float(details['max_difference_with_best_scores'].strip('%+')) if details['max_difference_with_best_scores'] is not None else 0.0,
        }
        global_data.append(global_record)
    
        for key, value in details.items():
            if key.endswith('.jpeg'):
                individual_record = {
                    'animal': entity,
                    'score_percentage': float(value['score_percentage'].strip('%')) if value['score_percentage'] is not None else 0.0,
                    'ranking': int(value['ranking'].split('/')[0]) if value['ranking'] is not None else 0
                }
                individual_data.append(individual_record)
    
    return global_data, individual_data

    
def make_bar_plot_avg_scores(global_df):
    # Define a color palette with 5 colors
    palette = sns.color_palette("husl", 5)

    # Bar plot for average scores
    plt.figure(figsize=(15, 8))
    sns.barplot(x='animal', y='average_scores_percentage', data=global_df, palette=palette)
    plt.title('Average Score Percentage by Animal')
    plt.xlabel('Animal')
    plt.ylabel('Average Score (%)')
    plt.xticks(rotation=90)

    # Get current y-axis limits
    ymin, ymax = plt.gca().get_ylim()

    # Adding dashed lines every 10% within the current y-axis limits
    for y in range(int(ymin), int(ymax)+1, 10):
        plt.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)
    
    # Save the image
    plt.savefig('docs/models_performances/evaluations/average_score_barplot.png', bbox_inches='tight')
    plt.show()
    
    
def make_bar_plot_avg_difference_best_scores(global_df):
    # Define a color palette with 5 colors
    palette = sns.color_palette("husl", 5)
    
    # Bar plot for average difference with best scores
    plt.figure(figsize=(15, 8))
    sns.barplot(x='animal', y='average_difference_with_best_scores', data=global_df, palette=palette)
    plt.title('Average Difference with Best Scores by Animal')
    plt.xlabel('Animal')
    plt.ylabel('Average Difference with Best Scores (%)')
    plt.xticks(rotation=90)

    # Get current y-axis limits
    ymin, ymax = plt.gca().get_ylim()

    # Adding dashed lines every 10% within the current y-axis limits
    for y in range(int(ymin), int(ymax)+1, 10):
        plt.axhline(y=y, color='gray', linestyle='--', linewidth=0.5)
    
    # Save the image
    plt.savefig('docs/models_performances/evaluations/average_difference_with_best_scores_barplot.png', bbox_inches='tight')
    plt.show()


def make_box_plot_avg_score_percentage(individual_df):
    # Define a color palette with 5 colors
    palette = sns.color_palette("husl", 5)
    
    # Box plot for score percentages
    plt.figure(figsize=(15, 8))
    sns.boxplot(x='animal', y='score_percentage', data=individual_df, palette=palette)
    plt.title('Score Percentage Distribution by Animal')
    plt.xlabel('Animal')
    plt.ylabel('Score (%)')
    plt.xticks(rotation=90)

    # Save the image
    plt.savefig('docs/models_performances/evaluations/score_distribution_boxplot.png', bbox_inches='tight')
    plt.show()
    
    
def make_box_plot_avg_rankings(individual_df):
    # Define a color palette with 5 colors
    palette = sns.color_palette("husl", 5)
    
    # Box plot for rankings
    plt.figure(figsize=(15, 8))
    sns.boxplot(x='animal', y='ranking', data=individual_df, palette=palette)
    plt.title('Ranking Distribution by Animal')
    plt.xlabel('Animal')
    plt.ylabel('Ranking')
    plt.xticks(rotation=90)

    # Invert the y-axis
    plt.gca().invert_yaxis()
    
    # Save the image
    plt.savefig('docs/models_performances/evaluations/ranking_distribution_boxplot.png', bbox_inches='tight')
    plt.show()
