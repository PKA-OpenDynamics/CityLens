// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { useRef, useState } from 'react';
import {
  Animated,
  PanResponder,
  StyleSheet,
  TouchableOpacity,
  View,
  Text,
} from 'react-native';
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
      <TouchableOpacity
        style={styles.mainButton}
        activeOpacity={0.85}
        onPress={onPress}
      >
        <MaterialIcons name="smart-toy" size={22} color="#FFFFFF" />
        <Text style={styles.label}>AI CityLens</Text>
      </TouchableOpacity>
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
    backgroundColor: '#20A957',
    borderRadius: 999,
    paddingHorizontal: 14,
    paddingVertical: 8,
    shadowColor: '#000',
    shadowOpacity: 0.2,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
    elevation: 4,
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


