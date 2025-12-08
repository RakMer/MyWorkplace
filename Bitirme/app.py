from flask import Flask, render_template, jsonify, request
import json
import logging
from spark_queries import (
    get_spark_session, 
    get_dataframe,
    query_ai_articles,
    query_top_stories,
    query_statistics,
    query_top_authors,
    query_top_articles_by_points,
    query_articles,
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global değişkenler
spark = None
df = None

def init_spark():
    """Spark ve DataFrame'ı başlat"""
    global spark, df
    if spark is None:
        spark = get_spark_session()
        df = get_dataframe(spark)
    return spark, df

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')

@app.route('/api/statistics', methods=['GET'])
def api_statistics():
    """İstatistikler API endpoint'i"""
    try:
        spark, df = init_spark()
        stats = query_statistics(df)
        return jsonify({
            "success": True,
            "data": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/ai-articles', methods=['GET'])
def api_ai_articles():
    """AI makaleleri API endpoint'i"""
    try:
        spark, df = init_spark()
        limit = request.args.get('limit', 50, type=int)
        articles = query_ai_articles(df, limit)
        return jsonify({
            "success": True,
            "data": articles,
            "count": len(articles)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/top-stories', methods=['GET'])
def api_top_stories():
    """En çok yoruma sahip hikayeler API endpoint'i"""
    try:
        spark, df = init_spark()
        limit = request.args.get('limit', 10, type=int)
        stories = query_top_stories(df, limit)
        return jsonify({
            "success": True,
            "data": stories,
            "count": len(stories)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/top-authors', methods=['GET'])
def api_top_authors():
    """En çok haber yazan yazarlar API endpoint'i"""
    try:
        spark, df = init_spark()
        limit = request.args.get('limit', 10, type=int)
        authors = query_top_authors(df, limit)
        return jsonify({
            "success": True,
            "data": authors,
            "count": len(authors)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/top-articles', methods=['GET'])
def api_top_articles():
    """En yüksek puan alan makaleler API endpoint'i"""
    try:
        spark, df = init_spark()
        limit = request.args.get('limit', 10, type=int)
        articles = query_top_articles_by_points(df, limit)
        return jsonify({
            "success": True,
            "data": articles,
            "count": len(articles)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/articles', methods=['GET'])
def api_articles():
    """Başlığa, yazara ve tarihe göre arama"""
    try:
        spark, df = init_spark()
        keyword = request.args.get('keyword')
        author = request.args.get('author')
        sort = request.args.get('sort', 'date_desc')
        limit = request.args.get('limit', 20, type=int)

        articles = query_articles(df, keyword=keyword, author=author, sort=sort, limit=limit)

        return jsonify({
            "success": True,
            "data": articles,
            "count": len(articles)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/all-data', methods=['GET'])
def api_all_data():
    """Tüm verileri bir seferde getir"""
    try:
        logger.info("API all-data çağrıldı")
        spark, df = init_spark()
        logger.info("Spark başlatıldı")
        
        logger.info("İstatistikler hesaplanıyor...")
        stats = query_statistics(df)
        logger.info(f"İstatistikler: {stats}")
        
        logger.info("AI makaleleri çekiliyor...")
        ai_articles = query_ai_articles(df, 20)
        logger.info(f"AI makaleleri: {len(ai_articles)} bulundu")
        
        logger.info("Top stories çekiliyor...")
        top_stories = query_top_stories(df, 10)
        logger.info(f"Top stories: {len(top_stories)} bulundu")
        
        logger.info("Top authors çekiliyor...")
        top_authors = query_top_authors(df, 10)
        logger.info(f"Top authors: {len(top_authors)} bulundu")
        
        logger.info("Top articles çekiliyor...")
        top_articles = query_top_articles_by_points(df, 10)
        logger.info(f"Top articles: {len(top_articles)} bulundu")
        
        data = {
            "statistics": stats,
            "ai_articles": ai_articles,
            "top_stories": top_stories,
            "top_authors": top_authors,
            "top_articles": top_articles
        }
        
        logger.info("Tüm veriler başarıyla toplandı")
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        logger.error(f"Hata oluştu: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404 hatası"""
    return jsonify({"error": "Sayfa bulunamadı"}), 404

@app.errorhandler(500)
def internal_error(error):
    """500 hatası"""
    return jsonify({"error": "Sunucu hatası"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8765)
