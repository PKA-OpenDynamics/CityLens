// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { useRef, useState, useEffect } from 'react';
import {
  Animated,
  PanResponder,
  StyleSheet,
  TouchableOpacity,
  View,
  Text,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons } from '@expo/vector-icons';

type Props = {
  onPress: () => void;
};

/**
 * Nút AI nổi có thể kéo, có nhãn "AI CityLens" và nút X để ẩn tạm.
 * Trạng thái ẩn chỉ áp dụng trong lần mở Explore hiện tại;
 * khi rời Explore rồi quay lại, nút sẽ hiện lại.
 */

const FloatingAIButton: React.FC<Props> = ({ onPress }) => {
  const [visible, setVisible] = useState(true);
  const pan = useRef(new Animated.ValueXY({ x: 16, y: 500 })).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    );
    pulse.start();
    return () => pulse.stop();
  }, []);

  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onPanResponderGrant: () => {
        pan.setOffset({
          x: (pan as any).x._value,
          y: (pan as any).y._value,
        });
      },
      onPanResponderMove: Animated.event(
        [null, { dx: pan.x, dy: pan.y }],
        { useNativeDriver: false },
      ),
      onPanResponderRelease: () => {
        pan.flattenOffset();
      },
    }),
  ).current;

  if (!visible) return null;

  return (
    <Animated.View
      style={[styles.container, pan.getLayout()]}
      {...panResponder.panHandlers}
    >
      <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
        <TouchableOpacity
          activeOpacity={0.85}
          onPress={onPress}
        >
          <LinearGradient
            colors={['#20A957', '#7BE882']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.mainButton}
          >
            <MaterialIcons name="auto-awesome" size={22} color="#FFFFFF" />
            <Text style={styles.label}>AI CityLens</Text>
          </LinearGradient>
        </TouchableOpacity>
      </Animated.View>
      <TouchableOpacity
        style={styles.closeButton}
        onPress={() => {
          setVisible(false);
        }}
        hitSlop={{ top: 6, bottom: 6, left: 6, right: 6 }}
      >
        <Text style={styles.closeText}>×</Text>
      </TouchableOpacity>
    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    zIndex: 30,
  },
  mainButton: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 999,
    paddingHorizontal: 16,
    paddingVertical: 10,
    shadowColor: '#20A957',
    shadowOpacity: 0.4,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 8,
    elevation: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  label: {
    marginLeft: 6,
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '600',
  },
  closeButton: {
    position: 'absolute',
    top: -6,
    right: -6,
    width: 18,
    height: 18,
    borderRadius: 9,
    backgroundColor: '#111827',
    alignItems: 'center',
    justifyContent: 'center',
  },
  closeText: {
    color: '#FFFFFF',
    fontSize: 12,
    lineHeight: 12,
  },
});

export default FloatingAIButton;


