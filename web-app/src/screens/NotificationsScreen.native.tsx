// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { alertsService, AlertItem } from '../services/alerts';

const NotificationsScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const [loading, setLoading] = useState(false);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const data = await alertsService.list();
      setAlerts(data);
    } catch (err) {
      console.warn('Fetch alerts failed', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backButton}>
          <MaterialIcons name="arrow-back" size={22} color="#20A957" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Thông báo</Text>
        <TouchableOpacity onPress={loadAlerts} style={styles.backButton}>
          <MaterialIcons name="refresh" size={22} color="#20A957" />
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={styles.loadingBox}>
          <ActivityIndicator size="large" color="#20A957" />
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.list}>
          {alerts.length === 0 ? (
            <Text style={styles.emptyText}>Chưa có thông báo</Text>
          ) : (
            alerts.map((a) => (
              <View key={a._id} style={styles.card}>
                <View style={styles.cardHeader}>
                  <MaterialIcons name="campaign" size={20} color="#20A957" />
                  <Text style={styles.cardTitle}>{a.title}</Text>
                </View>
                {a.description ? <Text style={styles.cardDesc}>{a.description}</Text> : null}
                <View style={styles.metaRow}>
                  {a.type ? <Text style={styles.tag}>Loại: {a.type}</Text> : null}
                  {a.ward ? <Text style={styles.tag}>Phường: {a.ward}</Text> : null}
                  {a.severity ? <Text style={styles.tag}>Mức: {a.severity}</Text> : null}
                </View>
                {a.updatedAt ? (
                  <Text style={styles.timeText}>
                    {new Date(a.updatedAt).toLocaleString('vi-VN')}
                  </Text>
                ) : null}
              </View>
            ))
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#E5E7EB',
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#20A957',
  },
  loadingBox: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  list: {
    padding: 16,
    gap: 12,
  },
  emptyText: {
    textAlign: 'center',
    color: '#6B7280',
    marginTop: 24,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 14,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 3,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 4,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#111827',
    flex: 1,
  },
  cardDesc: {
    color: '#374151',
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 6,
  },
  metaRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 4,
  },
  tag: {
    fontSize: 12,
    color: '#065F46',
    backgroundColor: '#ECFDF3',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  timeText: {
    fontSize: 12,
    color: '#6B7280',
  },
});

export default NotificationsScreen;

