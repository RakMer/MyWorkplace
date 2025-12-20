import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'dart:io';

void main() {
  runApp(const AkaryakitApp());
}

class AkaryakitApp extends StatelessWidget {
  const AkaryakitApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Akaryakıt Fiyatları',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6366F1),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        fontFamily: 'SF Pro Display',
        cardTheme: CardThemeData(
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 0,
        ),
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6366F1),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
        fontFamily: 'SF Pro Display',
      ),
      home: const HomeScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

// ============================================================================
// VERİ MODELLERİ
// ============================================================================

class CityFuelPrice {
  final String sehir;
  final String? ilce;
  final double benzin;
  final double motorin;

  CityFuelPrice({
    required this.sehir,
    this.ilce,
    required this.benzin,
    required this.motorin,
  });

  factory CityFuelPrice.fromJson(Map<String, dynamic> json) {
    return CityFuelPrice(
      sehir: json['sehir'] ?? '',
      ilce: json['ilce'],
      benzin: (json['benzin'] ?? 0).toDouble(),
      motorin: (json['motorin'] ?? 0).toDouble(),
    );
  }
}

class CompanyData {
  final String kaynak;
  final String sonGuncelleme;
  final List<CityFuelPrice> veriler;

  CompanyData({
    required this.kaynak,
    required this.sonGuncelleme,
    required this.veriler,
  });

  factory CompanyData.fromJson(Map<String, dynamic> json) {
    var list = json['veriler'] as List;
    List<CityFuelPrice> veriler = list.map((i) => CityFuelPrice.fromJson(i)).toList();
    
    return CompanyData(
      kaynak: json['kaynak'] ?? '',
      sonGuncelleme: json['son_guncelleme'] ?? '',
      veriler: veriler,
    );
  }
}

class FuelPrice {
  final String companyName;
  final double gasPrice;
  final double dieselPrice;
  final String logoUrl;
  final String lastUpdate;

  FuelPrice({
    required this.companyName,
    required this.gasPrice,
    required this.dieselPrice,
    required this.logoUrl,
    required this.lastUpdate,
  });
}

// ============================================================================
// VERİ SERVİSİ
// ============================================================================

class FuelDataService {
  static Future<List<FuelPrice>> loadFuelPrices(String selectedCity) async {
    List<FuelPrice> prices = [];

    // Şirket - Dosya eşleştirmesi
    Map<String, String> companyFiles = {
      'Opet': 'opet_fiyatlari.json',
      'Petrol Ofisi': 'petrol_ofisi_fiyatlari.json',
      'Shell': 'shell_fiyatlari.json',
      'Total': 'total_fiyatlari.json',
      'Lukoil': 'lukoil_fiyatlari.json',
      'TP': 'tp_fiatlari.json',
    };

    // Logo dosyaları
    Map<String, String> logos = {
      'Opet': 'assets/logos/OpetLogo.jpg',
      'Petrol Ofisi': 'assets/logos/PetrolOfisiLogo.png',
      'Shell': 'assets/logos/ShellLogo.png',
      'Total': 'assets/logos/TotalLogo.png',
      'Lukoil': 'assets/logos/LukoilLogo.svg.png',
      'TP': 'assets/logos/TPLogo.png',
    };

    for (var entry in companyFiles.entries) {
      try {
        String jsonString = await rootBundle.loadString('assets/${entry.value}');
        Map<String, dynamic> jsonData = json.decode(jsonString);
        CompanyData companyData = CompanyData.fromJson(jsonData);

        // Şehir adını normalize et
        String normalizedCity = selectedCity.toUpperCase().trim();
        
        // Seçili şehir için veriyi bul
        CityFuelPrice? cityPrice = companyData.veriler.firstWhere(
          (price) {
            String priceSehir = price.sehir.toUpperCase().trim();
            // İstanbul için özel kontrol
            if (normalizedCity.contains('ISTANBUL') || normalizedCity.contains('İSTANBUL')) {
              return priceSehir.contains('ISTANBUL') || priceSehir.contains('İSTANBUL');
            }
            return priceSehir.contains(normalizedCity);
          },
          orElse: () => companyData.veriler.isNotEmpty 
              ? companyData.veriler.first 
              : CityFuelPrice(sehir: '', benzin: 0, motorin: 0),
        );

        if (cityPrice.benzin > 0 && cityPrice.motorin > 0) {
          prices.add(FuelPrice(
            companyName: entry.key,
            gasPrice: cityPrice.benzin,
            dieselPrice: cityPrice.motorin,
            logoUrl: logos[entry.key] ?? '',
            lastUpdate: companyData.sonGuncelleme,
          ));
        }
      } catch (e) {
        print('Hata ${entry.key}: $e');
      }
    }

    return prices;
  }

  static Future<List<String>> loadAvailableCities() async {
    try {
      String jsonString = await rootBundle.loadString('assets/opet_fiyatlari.json');
      Map<String, dynamic> jsonData = json.decode(jsonString);
      CompanyData companyData = CompanyData.fromJson(jsonData);
      
      List<String> cities = companyData.veriler
          .map((e) => e.sehir)
          .where((city) => city.isNotEmpty)
          .toSet()
          .toList();
      
      cities.sort();
      return cities;
    } catch (e) {
      print('Şehir listesi yüklenemedi: $e');
      return ['İSTANBUL', 'ANKARA', 'İZMİR'];
    }
  }
}

// ============================================================================
// ANA SAYFA (HomeScreen)
// ============================================================================

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<FuelPrice> fuelPrices = [];
  List<String> availableCities = [];
  String selectedCity = 'İSTANBUL';
  bool isLoading = true;
  bool hasInternet = true;

  @override
  void initState() {
    super.initState();
    _checkInternetAndLoad();
  }

  Future<void> _checkInternetAndLoad() async {
    await _checkInternetConnection();
    if (hasInternet) {
      await _loadSavedCity();
    } else {
      setState(() => isLoading = false);
    }
  }

  Future<void> _checkInternetConnection() async {
    // Asset dosyaları local olduğu için her zaman erişilebilir
    // Eğer ilerleye API'den veri çekilecekse bu method güncellenebilir
    setState(() {
      hasInternet = true;
    });
  }

  Future<void> _loadSavedCity() async {
    // Kaydedilmiş şehri yükle
    final prefs = await SharedPreferences.getInstance();
    final savedCity = prefs.getString('selected_city');
    
    if (savedCity != null && savedCity.isNotEmpty) {
      setState(() {
        selectedCity = savedCity;
      });
    }
    
    _loadData();
  }

  Future<void> _saveCity(String city) async {
    // Şehri kaydet
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('selected_city', city);
  }

  Future<void> _loadData() async {
    setState(() => isLoading = true);
    
    await _checkInternetConnection();
    
    if (hasInternet) {
      availableCities = await FuelDataService.loadAvailableCities();
      fuelPrices = await FuelDataService.loadFuelPrices(selectedCity);
    }
    
    setState(() => isLoading = false);
  }

  Future<void> _changeCity() async {
    String? newCity = await showDialog<String>(
      context: context,
      builder: (context) => CitySelectionDialog(
        cities: availableCities,
        selectedCity: selectedCity,
      ),
    );

    if (newCity != null && newCity != selectedCity) {
      setState(() {
        selectedCity = newCity;
        isLoading = true;
      });
      
      // Yeni şehri kaydet
      await _saveCity(newCity);
      
      fuelPrices = await FuelDataService.loadFuelPrices(selectedCity);
      
      setState(() => isLoading = false);
      
      // Kullanıcıya bilgi ver
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.white),
                const SizedBox(width: 8),
                Text('$newCity şehri kaydedildi'),
              ],
            ),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        backgroundColor: colorScheme.surface,
        body: CustomScrollView(
          slivers: [
            // Modern App Bar
            SliverAppBar(
              expandedHeight: 200,
              floating: false,
              pinned: true,
              flexibleSpace: FlexibleSpaceBar(
                background: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        colorScheme.primary,
                        colorScheme.primary.withOpacity(0.7),
                        colorScheme.secondary,
                      ],
                    ),
                  ),
                  child: SafeArea(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const SizedBox(height: 20),
                        const Icon(
                          Icons.local_gas_station_rounded,
                          size: 48,
                          color: Colors.white,
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'Akaryakıt Fiyatları',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        // Şehir Seçici
                        GestureDetector(
                          onTap: _changeCity,
                          child: Container(
                            margin: const EdgeInsets.symmetric(horizontal: 24),
                            padding: const EdgeInsets.symmetric(
                              horizontal: 20,
                              vertical: 12,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(30),
                              border: Border.all(
                                color: Colors.white.withOpacity(0.3),
                                width: 1,
                              ),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(
                                  Icons.location_on_rounded,
                                  color: Colors.white,
                                  size: 20,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  selectedCity,
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                const Icon(
                                  Icons.keyboard_arrow_down_rounded,
                                  color: Colors.white,
                                  size: 20,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                title: const Text(''),
              ),
              actions: [
                IconButton(
                  icon: const Icon(Icons.refresh_rounded),
                  onPressed: _loadData,
                  tooltip: 'Yenile',
                ),
              ],
            ),
            
            // Tab Bar
            SliverPersistentHeader(
              pinned: true,
              delegate: _StickyTabBarDelegate(
                TabBar(
                  indicatorSize: TabBarIndicatorSize.label,
                  indicatorWeight: 3,
                  indicatorColor: colorScheme.primary,
                  labelColor: colorScheme.primary,
                  unselectedLabelColor: colorScheme.onSurface.withOpacity(0.6),
                  labelStyle: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                  tabs: const [
                    Tab(
                      icon: Icon(Icons.local_gas_station_rounded),
                      text: 'Benzin',
                    ),
                    Tab(
                      icon: Icon(Icons.local_shipping_rounded),
                      text: 'Motorin',
                    ),
                  ],
                ),
              ),
            ),
            
            // Content
            SliverFillRemaining(
              child: !hasInternet
                  ? _buildNoInternetWidget()
                  : isLoading
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              CircularProgressIndicator(
                                color: colorScheme.primary,
                              ),
                              const SizedBox(height: 16),
                              Text(
                                'Fiyatlar yükleniyor...',
                                style: TextStyle(
                                  color: colorScheme.onSurface.withOpacity(0.6),
                                ),
                              ),
                            ],
                          ),
                        )
                      : TabBarView(
                          children: [
                            _buildFuelList(fuelPrices, isGasoline: true),
                            _buildFuelList(fuelPrices, isGasoline: false),
                          ],
                        ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFuelList(List<FuelPrice> prices, {required bool isGasoline}) {
    final colorScheme = Theme.of(context).colorScheme;
    
    if (prices.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline_rounded,
              size: 64,
              color: colorScheme.onSurface.withOpacity(0.3),
            ),
            const SizedBox(height: 16),
            Text(
              'Veri bulunamadı',
              style: TextStyle(
                fontSize: 18,
                color: colorScheme.onSurface.withOpacity(0.6),
              ),
            ),
          ],
        ),
      );
    }

    // Fiyata göre sırala
    List<FuelPrice> sortedPrices = List.from(prices);
    sortedPrices.sort((a, b) {
      double priceA = isGasoline ? a.gasPrice : a.dieselPrice;
      double priceB = isGasoline ? b.gasPrice : b.dieselPrice;
      return priceA.compareTo(priceB);
    });

    // İstatistikler
    double average = sortedPrices
        .map((p) => isGasoline ? p.gasPrice : p.dieselPrice)
        .reduce((a, b) => a + b) / sortedPrices.length;
    double minPrice = isGasoline 
        ? sortedPrices.first.gasPrice 
        : sortedPrices.first.dieselPrice;
    double maxPrice = isGasoline 
        ? sortedPrices.last.gasPrice 
        : sortedPrices.last.dieselPrice;

    return Column(
      children: [
        // İstatistik Kartları
        Container(
          margin: const EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  title: 'Ortalama',
                  value: '${average.toStringAsFixed(2)} ₺',
                  icon: Icons.analytics_rounded,
                  gradient: LinearGradient(
                    colors: [
                      colorScheme.primary.withOpacity(0.8),
                      colorScheme.primary,
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  title: 'En Ucuz',
                  value: '${minPrice.toStringAsFixed(2)} ₺',
                  icon: Icons.trending_down_rounded,
                  gradient: const LinearGradient(
                    colors: [Color(0xFF10B981), Color(0xFF059669)],
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatCard(
                  title: 'En Pahalı',
                  value: '${maxPrice.toStringAsFixed(2)} ₺',
                  icon: Icons.trending_up_rounded,
                  gradient: const LinearGradient(
                    colors: [Color(0xFFEF4444), Color(0xFFDC2626)],
                  ),
                ),
              ),
            ],
          ),
        ),

        // Firma Listesi
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            itemCount: sortedPrices.length,
            itemBuilder: (context, index) {
              FuelPrice price = sortedPrices[index];
              double currentPrice = isGasoline ? price.gasPrice : price.dieselPrice;
              bool isCheapest = index == 0;
              bool isMostExpensive = index == sortedPrices.length - 1;

              return TweenAnimationBuilder<double>(
                duration: Duration(milliseconds: 300 + (index * 50)),
                tween: Tween(begin: 0.0, end: 1.0),
                builder: (context, value, child) {
                  return Transform.scale(
                    scale: 0.95 + (value * 0.05),
                    child: Opacity(
                      opacity: value,
                      child: child,
                    ),
                  );
                },
                child: Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  decoration: BoxDecoration(
                    gradient: isCheapest
                        ? LinearGradient(
                            colors: [
                              const Color(0xFF10B981).withOpacity(0.1),
                              const Color(0xFF059669).withOpacity(0.05),
                            ],
                          )
                        : null,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: isCheapest
                          ? const Color(0xFF10B981).withOpacity(0.3)
                          : colorScheme.outline.withOpacity(0.1),
                      width: 1.5,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: isCheapest
                            ? const Color(0xFF10B981).withOpacity(0.1)
                            : Colors.black.withOpacity(0.03),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      borderRadius: BorderRadius.circular(20),
                      onTap: () {
                        // Detay sayfası eklenebilir
                      },
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          children: [
                            // Logo
                            Container(
                              width: 64,
                              height: 64,
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(16),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.black.withOpacity(0.05),
                                    blurRadius: 8,
                                    offset: const Offset(0, 2),
                                  ),
                                ],
                              ),
                              padding: const EdgeInsets.all(12),
                              child: Image.asset(
                                price.logoUrl,
                                fit: BoxFit.contain,
                                errorBuilder: (context, error, stackTrace) {
                                  return Icon(
                                    Icons.local_gas_station_rounded,
                                    size: 32,
                                    color: colorScheme.primary.withOpacity(0.5),
                                  );
                                },
                              ),
                            ),
                            const SizedBox(width: 16),
                            
                            // Firma Bilgileri
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Text(
                                        price.companyName,
                                        style: TextStyle(
                                          fontSize: 18,
                                          fontWeight: FontWeight.bold,
                                          color: colorScheme.onSurface,
                                        ),
                                      ),
                                      if (isCheapest) ...[
                                        const SizedBox(width: 8),
                                        Container(
                                          padding: const EdgeInsets.symmetric(
                                            horizontal: 8,
                                            vertical: 4,
                                          ),
                                          decoration: BoxDecoration(
                                            gradient: const LinearGradient(
                                              colors: [
                                                Color(0xFF10B981),
                                                Color(0xFF059669),
                                              ],
                                            ),
                                            borderRadius: BorderRadius.circular(8),
                                          ),
                                          child: const Text(
                                            '★ EN UCUZ',
                                            style: TextStyle(
                                              color: Colors.white,
                                              fontSize: 10,
                                              fontWeight: FontWeight.bold,
                                              letterSpacing: 0.5,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ],
                                  ),
                                  const SizedBox(height: 4),
                                  Row(
                                    children: [
                                      Icon(
                                        Icons.access_time_rounded,
                                        size: 14,
                                        color: colorScheme.onSurface.withOpacity(0.5),
                                      ),
                                      const SizedBox(width: 4),
                                      Text(
                                        price.lastUpdate,
                                        style: TextStyle(
                                          fontSize: 12,
                                          color: colorScheme.onSurface.withOpacity(0.6),
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                            
                            // Fiyat
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.end,
                              children: [
                                Text(
                                  '${currentPrice.toStringAsFixed(2)} ₺',
                                  style: TextStyle(
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                    color: isCheapest
                                        ? const Color(0xFF059669)
                                        : isMostExpensive
                                            ? const Color(0xFFDC2626)
                                            : colorScheme.onSurface,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: (isCheapest
                                            ? const Color(0xFF10B981)
                                            : isMostExpensive
                                                ? const Color(0xFFEF4444)
                                                : colorScheme.primary)
                                        .withOpacity(0.1),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    '${((currentPrice - minPrice) / minPrice * 100).toStringAsFixed(1)}%',
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.w600,
                                      color: isCheapest
                                          ? const Color(0xFF059669)
                                          : isMostExpensive
                                              ? const Color(0xFFDC2626)
                                              : colorScheme.primary,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required IconData icon,
    required Gradient gradient,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(icon, color: Colors.white, size: 24),
          const SizedBox(height: 8),
          Text(
            title,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 11,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNoInternetWidget() {
    final colorScheme = Theme.of(context).colorScheme;
    
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: colorScheme.errorContainer.withOpacity(0.3),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.wifi_off_rounded,
                size: 80,
                color: colorScheme.error,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'İnternet Bağlantısı Yok',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: colorScheme.onSurface,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              'Akaryakıt fiyatlarını görüntülemek için lütfen internet bağlantınızı kontrol edin.',
              style: TextStyle(
                fontSize: 16,
                color: colorScheme.onSurface.withOpacity(0.6),
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            FilledButton.icon(
              onPressed: () async {
                await _checkInternetAndLoad();
              },
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Tekrar Dene'),
              style: FilledButton.styleFrom(
                backgroundColor: colorScheme.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
                  vertical: 16,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ============================================================================
// STICKY TAB BAR DELEGATE
// ============================================================================

class _StickyTabBarDelegate extends SliverPersistentHeaderDelegate {
  final TabBar tabBar;

  _StickyTabBarDelegate(this.tabBar);

  @override
  double get minExtent => tabBar.preferredSize.height;

  @override
  double get maxExtent => tabBar.preferredSize.height;

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
      color: Theme.of(context).scaffoldBackgroundColor,
      child: tabBar,
    );
  }

  @override
  bool shouldRebuild(_StickyTabBarDelegate oldDelegate) {
    return tabBar != oldDelegate.tabBar;
  }
}

// ============================================================================
// ŞEHİR SEÇİM DİYALOGU
// ============================================================================

class CitySelectionDialog extends StatefulWidget {
  final List<String> cities;
  final String selectedCity;

  const CitySelectionDialog({
    super.key,
    required this.cities,
    required this.selectedCity,
  });

  @override
  State<CitySelectionDialog> createState() => _CitySelectionDialogState();
}

class _CitySelectionDialogState extends State<CitySelectionDialog> {
  String searchQuery = '';
  late TextEditingController _searchController;

  @override
  void initState() {
    super.initState();
    _searchController = TextEditingController();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    
    List<String> filteredCities = widget.cities
        .where((city) => city.toLowerCase().contains(searchQuery.toLowerCase()))
        .toList();

    return Dialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(28),
      ),
      child: Container(
        constraints: const BoxConstraints(maxHeight: 600, maxWidth: 400),
        child: Column(
          children: [
            // Header
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    colorScheme.primary,
                    colorScheme.primary.withOpacity(0.8),
                  ],
                ),
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(28),
                  topRight: Radius.circular(28),
                ),
              ),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(
                      Icons.location_city_rounded,
                      color: Colors.white,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 16),
                  const Expanded(
                    child: Text(
                      'Şehir Seçin',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close_rounded, color: Colors.white),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),

            // Search Bar
            Padding(
              padding: const EdgeInsets.all(16),
              child: TextField(
                controller: _searchController,
                autofocus: true,
                decoration: InputDecoration(
                  hintText: 'Şehir ara...',
                  prefixIcon: Icon(Icons.search_rounded, color: colorScheme.primary),
                  suffixIcon: searchQuery.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear_rounded),
                          onPressed: () {
                            _searchController.clear();
                            setState(() => searchQuery = '');
                          },
                        )
                      : null,
                  filled: true,
                  fillColor: colorScheme.surface,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide(color: colorScheme.outline),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide(
                      color: colorScheme.outline.withOpacity(0.3),
                    ),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide(color: colorScheme.primary, width: 2),
                  ),
                ),
                onChanged: (value) {
                  setState(() => searchQuery = value);
                },
              ),
            ),

            // Cities List
            Expanded(
              child: filteredCities.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.search_off_rounded,
                            size: 64,
                            color: colorScheme.onSurface.withOpacity(0.3),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Şehir bulunamadı',
                            style: TextStyle(
                              fontSize: 16,
                              color: colorScheme.onSurface.withOpacity(0.6),
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 8),
                      itemCount: filteredCities.length,
                      itemBuilder: (context, index) {
                        String city = filteredCities[index];
                        bool isSelected = city == widget.selectedCity;

                        return Padding(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          child: Material(
                            color: Colors.transparent,
                            child: InkWell(
                              borderRadius: BorderRadius.circular(16),
                              onTap: () => Navigator.pop(context, city),
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 16,
                                  vertical: 12,
                                ),
                                decoration: BoxDecoration(
                                  color: isSelected
                                      ? colorScheme.primary.withOpacity(0.1)
                                      : Colors.transparent,
                                  borderRadius: BorderRadius.circular(16),
                                  border: Border.all(
                                    color: isSelected
                                        ? colorScheme.primary.withOpacity(0.3)
                                        : Colors.transparent,
                                    width: 1.5,
                                  ),
                                ),
                                child: Row(
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.all(8),
                                      decoration: BoxDecoration(
                                        color: isSelected
                                            ? colorScheme.primary
                                            : colorScheme.surface,
                                        borderRadius: BorderRadius.circular(10),
                                      ),
                                      child: Icon(
                                        isSelected
                                            ? Icons.check_circle_rounded
                                            : Icons.location_on_rounded,
                                        color: isSelected
                                            ? Colors.white
                                            : colorScheme.primary,
                                        size: 20,
                                      ),
                                    ),
                                    const SizedBox(width: 16),
                                    Expanded(
                                      child: Text(
                                        city,
                                        style: TextStyle(
                                          fontSize: 16,
                                          fontWeight: isSelected
                                              ? FontWeight.bold
                                              : FontWeight.w500,
                                          color: isSelected
                                              ? colorScheme.primary
                                              : colorScheme.onSurface,
                                        ),
                                      ),
                                    ),
                                    if (isSelected)
                                      Container(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 8,
                                          vertical: 4,
                                        ),
                                        decoration: BoxDecoration(
                                          color: colorScheme.primary,
                                          borderRadius: BorderRadius.circular(8),
                                        ),
                                        child: const Text(
                                          'SEÇİLİ',
                                          style: TextStyle(
                                            color: Colors.white,
                                            fontSize: 10,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
