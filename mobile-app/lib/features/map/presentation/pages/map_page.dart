// Copyright (c) 2025 CityLens Contributors
// Licensed under the MIT License

import 'package:flutter/material.dart';

class MapPage extends StatefulWidget {
  const MapPage({super.key});

  @override
  State<MapPage> createState() => _MapPageState();
}

class _MapPageState extends State<MapPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bản đồ'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () {
              // TODO: Show filter dialog
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          // TODO: Add Google Maps widget here
          Container(
            color: Colors.grey[300],
            child: const Center(
              child: Text('Bản đồ sẽ được hiển thị ở đây'),
            ),
          ),
          Positioned(
            top: 16,
            left: 16,
            right: 16,
            child: Card(
              child: TextField(
                decoration: InputDecoration(
                  hintText: 'Tìm kiếm vị trí...',
                  prefixIcon: const Icon(Icons.search),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          // TODO: Navigate to create report
        },
        icon: const Icon(Icons.add),
        label: const Text('Báo cáo sự cố'),
      ),
    );
  }
}
