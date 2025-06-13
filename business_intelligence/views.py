from django.shortcuts import render
from .models import Movie
from django.db.models import Count
import plotly.express as px

def movie_dashboard(request):
    # Query 1: Menghitung jumlah film per genre
    genre_counts = Movie.objects.values('genre').annotate(count=Count('genre')).order_by('-count')
    
    # Query 2: Menghitung jumlah film per negara
    # Anda mungkin perlu menambahkan model 'country' jika belum ada
    # Asumsi kolom 'country' ada di model Movie
    country_counts = Movie.objects.values('country').annotate(count=Count('country')).order_by('-count')

    # Membuat grafik bar untuk genre
    fig_genre = px.bar(
        [item for item in genre_counts],
        x='genre',
        y='count',
        title='Jumlah Film Berdasarkan Genre'
    )
    chart_genre = fig_genre.to_html(full_html=False, include_plotlyjs='cdn')

    # Membuat grafik pie untuk negara
    fig_country = px.pie(
        [item for item in country_counts],
        names='country',
        values='count',
        title='Distribusi Film Berdasarkan Negara'
    )
    chart_country = fig_country.to_html(full_html=False, include_plotlyjs='cdn')

    context = {
        'chart_genre': chart_genre,
        'chart_country': chart_country
    }
    
    # Hapus 'business_intelligence/' dari path template
    return render(request, 'dashboard.html', context)