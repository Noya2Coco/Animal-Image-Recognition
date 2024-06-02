import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from evaluate_model import predictions_all_entities


def transform_format_data(data):
    entities_data = []

    for entity, details in data.items():
        record = {
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
        entities_data.append(record)
    
    return entities_data

    
def make_bar_plot_avg_scores(data):
    plt.figure(figsize=(12, 6))
    sns.barplot(x='animal', y='average_scores_percentage', data=data)
    plt.title('Average Score Percentage by Animal')
    plt.xlabel('Animal')
    plt.ylabel('Average Score Percentage')
    plt.xticks(rotation=90)
    plt.savefig('docs/models_performances/evaluations/average_scores_barplot.png', bbox_inches='tight')
    plt.show()
    
    
def make_bar_plot_avg_difference_best_scores(data):
    plt.figure(figsize=(12, 6))
    sns.barplot(x='animal', y='average_difference_with_best_scores', data=data)
    plt.title('Average Difference with Best Scores by Animal')
    plt.xlabel('Animal')
    plt.ylabel('Average Difference with Best Scores (%)')
    plt.xticks(rotation=90)
    plt.savefig('docs/models_performances/evaluations/average_scores_boxplot.png', bbox_inches='tight')
    plt.show()


def make_box_plot_avg_score_percentage(data):
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='animal', y='average_scores_percentage', data=data)
    plt.title('Distribution of Average Score Percentage by Animal')
    plt.xlabel('Animal')
    plt.ylabel('Average Score Percentage')
    plt.xticks(rotation=90)
    plt.savefig('docs/models_performances/evaluations/average_rankings_boxplot.png', bbox_inches='tight')
    plt.show()
    
    
def make_box_plot_avg_rankings(data):
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='animal', y='average_rankings', data=data)
    plt.title('Distribution of Average Rankings by Animal')
    plt.xlabel('Animal')
    plt.ylabel('Average Rankings')
    plt.xticks(rotation=90)
    plt.savefig('docs/models_performances/evaluations/average_difference_barplot.png', bbox_inches='tight')
    plt.show()
