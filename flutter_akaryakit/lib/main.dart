import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';

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
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
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

    // Logo URL'leri
    Map<String, String> logos = {
      'Opet': 'https://logo.clearbit.com/opet.com.tr',
      'Petrol Ofisi': 'https://logo.clearbit.com/po.com.tr',
      'Shell': 'https://logo.clearbit.com/shell.com',
      'Total': 'https://logo.clearbit.com/totalenergies.com',
      'Lukoil': 'https://logo.clearbit.com/lukoil.com',
      'TP': 'https://logo.clearbit.com/tppd.com.tr',
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

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => isLoading = true);
    
    availableCities = await FuelDataService.loadAvailableCities();
    fuelPrices = await FuelDataService.loadFuelPrices(selectedCity);
    
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
      
      fuelPrices = await FuelDataService.loadFuelPrices(selectedCity);
      
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Akaryakıt Fiyatları'),
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _loadData,
            ),
          ],
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Benzin', icon: Icon(Icons.local_gas_station)),
              Tab(text: 'Motorin', icon: Icon(Icons.local_shipping)),
            ],
          ),
        ),
        body: Column(
          children: [
            // Şehir Seçici
            InkWell(
              onTap: _changeCity,
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
                color: Colors.blue.shade50,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.location_on, color: Colors.blue, size: 24),
                    const SizedBox(width: 8),
                    Text(
                      selectedCity,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue,
                      ),
                    ),
                    const SizedBox(width: 8),
                    const Icon(Icons.arrow_drop_down, color: Colors.blue),
                  ],
                ),
              ),
            ),
            
            // İçerik
            Expanded(
              child: isLoading
                  ? const Center(child: CircularProgressIndicator())
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
    if (prices.isEmpty) {
      return const Center(
        child: Text('Veri bulunamadı'),
      );
    }

    // Fiyata göre sırala
    List<FuelPrice> sortedPrices = List.from(prices);
    sortedPrices.sort((a, b) {
      double priceA = isGasoline ? a.gasPrice : a.dieselPrice;
      double priceB = isGasoline ? b.gasPrice : b.dieselPrice;
      return priceA.compareTo(priceB);
    });

    // Ortalama hesapla
    double average = sortedPrices.map((p) => isGasoline ? p.gasPrice : p.dieselPrice).reduce((a, b) => a + b) / sortedPrices.length;

    return Column(
      children: [
        // Ortalama fiyat kartı
        Container(
          margin: const EdgeInsets.all(16),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.blue.shade400, Colors.blue.shade600],
            ),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              Column(
                children: [
                  const Text(
                    'Ortalama Fiyat',
                    style: TextStyle(color: Colors.white, fontSize: 16),
                  ),
                  Text(
                    '${average.toStringAsFixed(2)} ₺',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              Column(
                children: [
                  const Text(
                    'En Ucuz',
                    style: TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                  Text(
                    '${(isGasoline ? sortedPrices.first.gasPrice : sortedPrices.first.dieselPrice).toStringAsFixed(2)} ₺',
                    style: const TextStyle(
                      color: Colors.greenAccent,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),

        // Firma listesi
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: sortedPrices.length,
            itemBuilder: (context, index) {
              FuelPrice price = sortedPrices[index];
              double currentPrice = isGasoline ? price.gasPrice : price.dieselPrice;
              bool isCheapest = index == 0;

              return Card(
                elevation: isCheapest ? 6 : 2,
                color: isCheapest ? Colors.green.shade50 : null,
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  contentPadding: const EdgeInsets.all(12),
                  leading: Container(
                    width: 60,
                    height: 60,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(8),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.grey.shade300,
                          blurRadius: 4,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Image.network(
                      price.logoUrl,
                      errorBuilder: (context, error, stackTrace) {
                        return Icon(Icons.local_gas_station, size: 32, color: Colors.grey.shade400);
                      },
                    ),
                  ),
                  title: Text(
                    price.companyName,
                    style: TextStyle(
                      fontWeight: isCheapest ? FontWeight.bold : FontWeight.w600,
                      fontSize: 16,
                    ),
                  ),
                  subtitle: Text(
                    'Güncelleme: ${price.lastUpdate}',
                    style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                  ),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        '${currentPrice.toStringAsFixed(2)} ₺',
                        style: TextStyle(
                          fontSize: isCheapest ? 24 : 20,
                          fontWeight: FontWeight.bold,
                          color: isCheapest ? Colors.green.shade700 : Colors.black87,
                        ),
                      ),
                      if (isCheapest)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.green,
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: const Text(
                            'EN UCUZ',
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
              );
            },
          ),
        ),
      ],
    );
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

  @override
  Widget build(BuildContext context) {
    List<String> filteredCities = widget.cities
        .where((city) => city.toLowerCase().contains(searchQuery.toLowerCase()))
        .toList();

    return AlertDialog(
      title: const Text('Şehir Seçin'),
      content: SizedBox(
        width: double.maxFinite,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              decoration: const InputDecoration(
                hintText: 'Şehir ara...',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
              ),
              onChanged: (value) {
                setState(() => searchQuery = value);
              },
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                shrinkWrap: true,
                itemCount: filteredCities.length,
                itemBuilder: (context, index) {
                  String city = filteredCities[index];
                  bool isSelected = city == widget.selectedCity;
                  
                  return ListTile(
                    title: Text(city),
                    selected: isSelected,
                    selectedTileColor: Colors.blue.shade50,
                    leading: isSelected
                        ? const Icon(Icons.check_circle, color: Colors.blue)
                        : const Icon(Icons.location_city),
                    onTap: () => Navigator.pop(context, city),
                  );
                },
              ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('İptal'),
        ),
      ],
    );
  }
}
