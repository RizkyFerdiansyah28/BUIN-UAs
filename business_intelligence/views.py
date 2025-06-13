from django.shortcuts import render
from .models import Movie
from django.db.models import Count, Avg
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def movie_dashboard(request):
    # === Bagian Analisis Deskriptif ===
    genre_counts = Movie.objects.values('genre').annotate(count=Count('id')).order_by('-count')
    fig_genre = px.bar(
        [item for item in genre_counts],
        x='genre', y='count', title='Jumlah Film Berdasarkan Genre (Keseluruhan)'
    )
    chart_genre = fig_genre.to_html(full_html=False, include_plotlyjs='cdn')

    country_counts = Movie.objects.values('country').annotate(count=Count('id')).order_by('-count')
    fig_country = px.pie(
        [item for item in country_counts],
        names='country', values='count', title='Distribusi Film Berdasarkan Negara'
    )
    chart_country = fig_country.to_html(full_html=False, include_plotlyjs='cdn')

    # === Bagian Prediksi Popularitas Genre ===
    yearly_genre_counts = Movie.objects.values('year', 'genre').annotate(count=Count('id')).order_by('year')
    df_genre = pd.DataFrame(list(yearly_genre_counts))
    
    comparison_charts = []
    chart_prediction = "<div>Data tidak cukup untuk prediksi genre.</div>"

    if not df_genre.empty and 'year' in df_genre.columns and 'genre' in df_genre.columns:
        pivot_df = df_genre.pivot_table(index='year', columns='genre', values='count', fill_value=0)
        top_5_genres = df_genre.groupby('genre')['count'].sum().nlargest(5).index.tolist()
        
        if top_5_genres:
            pivot_df = pivot_df[top_5_genres]
            predictions = {}
            future_year_val = pivot_df.index.max() + 1
            future_year = np.array([[future_year_val]])

            for genre in top_5_genres:
                X_genre = pivot_df.index.values.reshape(-1, 1)
                y_genre = pivot_df[genre].values
                model_genre = LinearRegression()
                model_genre.fit(X_genre, y_genre)
                predicted_count = model_genre.predict(future_year)[0]
                predictions[genre] = max(0, round(predicted_count))

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=pivot_df.index, y=y_genre, mode='markers', name='Data Asli', marker=dict(color='blue')))
                fig.add_trace(go.Scatter(x=pivot_df.index, y=model_genre.predict(X_genre), mode='lines', name='Garis Tren', line=dict(color='red')))
                fig.update_layout(title=f'Analisis Tren Genre: {genre}', xaxis_title='Tahun', yaxis_title='Jumlah Film')
                comparison_charts.append(fig.to_html(full_html=False, include_plotlyjs='cdn'))

            pred_df = pd.DataFrame(list(predictions.items()), columns=['Genre', 'PredictedCount'])
            fig_prediction = px.bar(pred_df, x='Genre', y='PredictedCount', title=f'Prediksi Jumlah Film Populer untuk Tahun {future_year_val}')
            chart_prediction = fig_prediction.to_html(full_html=False, include_plotlyjs='cdn')

    # === Bagian BARU: 10 Film dengan Rating Tertinggi ===
    top_10_movies = Movie.objects.order_by('-rating')[:10]
    df_top_movies = pd.DataFrame(list(top_10_movies.values('title', 'rating')))

    fig_top_movies = px.bar(
        df_top_movies,
        x='rating',
        y='title',
        orientation='h', # Membuat bar chart horizontal
        title='10 Film dengan Rating Tertinggi',
        labels={'rating': 'Rating', 'title': 'Judul Film'}
    )
    # Mengatur urutan agar film dengan rating tertinggi berada di paling atas
    fig_top_movies.update_layout(yaxis={'categoryorder':'total ascending'})
    chart_title_performance = fig_top_movies.to_html(full_html=False, include_plotlyjs='cdn')


    # Menyiapkan context untuk dikirim ke template
    context = {
        'chart_genre': chart_genre,
        'chart_country': chart_country,
        'chart_prediction': chart_prediction,
        'comparison_charts': comparison_charts,
        'chart_title_performance': chart_title_performance,
    }
    
    return render(request, 'dashboard.html', context)