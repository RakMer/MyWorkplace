// HackerNews Spark Analizi - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    loadAllData();

    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            await runSearch();
        });
    }
});

function showLoading() {
    document.getElementById('loading-spinner').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading-spinner').classList.add('hidden');
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = `❌ Hata: ${message}`;
    errorDiv.classList.remove('hidden');
    setTimeout(() => {
        errorDiv.classList.add('hidden');
    }, 5000);
}

async function runSearch() {
    const container = document.getElementById('search-results');
    if (!container) return;

    container.classList.add('loading');
    container.innerHTML = '<p>Arama yapılıyor...</p>';

    const keyword = document.getElementById('keyword')?.value.trim();
    const author = document.getElementById('author')?.value.trim();
    const sort = document.getElementById('sort')?.value || 'date_desc';

    const params = new URLSearchParams();
    if (keyword) params.append('keyword', keyword);
    if (author) params.append('author', author);
    if (sort) params.append('sort', sort);

    try {
        const response = await fetch(`/api/articles?${params.toString()}`);
        const result = await response.json();

        if (!result.success) {
            showError(result.error || 'Arama başarısız');
            container.classList.remove('loading');
            return;
        }

        displaySearchResults(result.data || []);
    } catch (error) {
        console.error('Arama hatası:', error);
        showError('Sunucuya bağlanılamadı');
    } finally {
        container.classList.remove('loading');
    }
}

async function loadAllData() {
    showLoading();
    try {
        const response = await fetch('/api/all-data');
        const result = await response.json();

        if (!result.success) {
            showError(result.error);
            hideLoading();
            return;
        }

        const data = result.data;

        // İstatistikler
        displayStatistics(data.statistics);

        // AI Makaleleri
        displayAIArticles(data.ai_articles);

        // En Çok Yorumlanan Hikayeler
        displayTopStories(data.top_stories);

        // En Çok Yazar
        displayTopAuthors(data.top_authors);

        // En Yüksek Puan Alan Makaleler
        displayTopArticles(data.top_articles);

        hideLoading();
    } catch (error) {
        console.error('Veri yükleme hatası:', error);
        showError('Sunucuya bağlanılamadı');
        hideLoading();
    }
}

function displayStatistics(stats) {
    document.getElementById('total-articles').textContent = 
        stats.total.toLocaleString('tr-TR');
    document.getElementById('with-author').textContent = 
        stats.with_author.toLocaleString('tr-TR');

    document.querySelectorAll('.stat-card').forEach(card => {
        card.classList.remove('loading');
    });
}

function displayAIArticles(articles) {
    const container = document.getElementById('ai-articles');
    container.innerHTML = '';

    if (articles.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1;">AI ile ilgili makale bulunamadı</p>';
        return;
    }

    articles.forEach((article, index) => {
        const card = createArticleCard(article, index);
        container.appendChild(card);
    });

    container.classList.remove('loading');
}

function displayTopStories(stories) {
    const container = document.getElementById('top-stories');
    container.innerHTML = '';

    if (stories.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1;">Hikaye bulunamadı</p>';
        return;
    }

    stories.forEach((story, index) => {
        const card = document.createElement('div');
        card.className = 'data-card';
        const storyId = story.story_id ? escapeHtml(String(story.story_id)) : 'N/A';
        const commentCount = story.comment_count || 0;
        card.innerHTML = `
            <h4>Hikaye #${index + 1}</h4>
            <p class="label">Story ID</p>
            <p class="story-id">${storyId}</p>
            <p class="label">Yorum Sayısı</p>
            <p class="value">${commentCount.toLocaleString('tr-TR')}</p>
        `;
        container.appendChild(card);
    });

    container.classList.remove('loading');
}

function displayTopAuthors(authors) {
    const container = document.getElementById('top-authors');
    container.innerHTML = '';

    if (authors.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1;">Yazar bulunamadı</p>';
        return;
    }

    authors.forEach((author, index) => {
        const card = document.createElement('div');
        card.className = 'data-card';
        const authorName = author.author ? escapeHtml(String(author.author)) : 'Bilinmeyen';
        const count = author.article_count || 0;
        card.innerHTML = `
            <h4>#${index + 1} - ${authorName}</h4>
            <p class="label">Makale Sayısı</p>
            <p class="value">${count.toLocaleString('tr-TR')}</p>
        `;
        container.appendChild(card);
    });

    container.classList.remove('loading');
}

function displayTopArticles(articles) {
    const container = document.getElementById('top-articles');
    container.innerHTML = '';

    if (articles.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1;">Makale bulunamadı</p>';
        return;
    }

    articles.forEach((article, index) => {
        const card = document.createElement('div');
        card.className = 'data-card';
        const title = article.title ? escapeHtml(String(article.title)) : 'Başlık yok';
        const points = article.points || 0;
        card.innerHTML = `
            <h4>#${index + 1} - ${title}</h4>
            <p class="label">Puan</p>
            <p class="value">${points.toLocaleString('tr-TR')}</p>
        `;
        container.appendChild(card);
    });

    container.classList.remove('loading');
}

function displaySearchResults(articles) {
    const container = document.getElementById('search-results');
    if (!container) return;

    container.innerHTML = '';

    if (!articles || articles.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1;">Sonuç bulunamadı</p>';
        return;
    }

    articles.forEach((article, index) => {
        const card = document.createElement('div');
        card.className = 'data-card';
        const title = article.title ? escapeHtml(String(article.title)) : 'Başlık yok';
        const author = article.author ? escapeHtml(String(article.author)) : 'Bilinmeyen';
        const points = article.points || 0;
        const createdAt = article.created_at ? new Date(article.created_at).toLocaleString('tr-TR') : 'Tarih yok';

        card.innerHTML = `
            <h4>#${index + 1} - ${title}</h4>
            <p class="label">Yazar</p>
            <p>${author}</p>
            <p class="label">Puan</p>
            <p class="value">${points.toLocaleString('tr-TR')}</p>
            <p class="label">Tarih</p>
            <p>${createdAt}</p>
        `;

        container.appendChild(card);
    });

    container.classList.remove('loading');
}

function createArticleCard(article, index) {
    const card = document.createElement('div');
    card.className = 'data-card';
    
    const title = article.title ? escapeHtml(String(article.title)) : 'Başlık yok';
    const author = article.author ? escapeHtml(String(article.author)) : 'Bilinmeyen';
    
    card.innerHTML = `
        <h4>#${index + 1} - ${title}</h4>
        <p class="label">Yazar</p>
        <p>${author}</p>
    `;
    
    return card;
}

function escapeHtml(text) {
    if (!text) return 'N/A';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Refresh butonu (opsiyonel)
function refreshData() {
    loadAllData();
}
