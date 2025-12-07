// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React from 'react';
import { View, Image, Text, StyleSheet, TouchableOpacity } from 'react-native';

interface AvatarProps {
  uri?: string;
  name?: string;
  size?: number;
  onPress?: () => void;
}

const getInitials = (name?: string): string => {
  if (!name) return '?';
  const words = name.trim().split(/\s+/);
  if (words.length === 0) return '?';
  if (words.length === 1) return words[0].charAt(0).toUpperCase();
  return (words[0].charAt(0) + words[words.length - 1].charAt(0)).toUpperCase();
};

const getAvatarColor = (name?: string): string => {
  if (!name) return '#20A957';
  const colors = [
    '#20A957', '#3B82F6', '#8B5CF6', '#EC4899', '#F59E0B',
    '#EF4444', '#10B981', '#06B6D4', '#F97316', '#6366F1',
  ];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
};

const Avatar: React.FC<AvatarProps> = ({ 
  uri,
  name,
  size = 40,
  onPress 
}) => {
  const containerStyle = {
    width: size,
    height: size,
    borderRadius: size / 2,
  };

  const initials = getInitials(name);
  const backgroundColor = getAvatarColor(name);
  const fontSize = size * 0.4;

  const renderContent = () => {
    if (uri) {
      return <Image source={{ uri }} style={[styles.image, containerStyle]} />;
    }
    return (
      <View style={[styles.initialsContainer, containerStyle, { backgroundColor }]}>
        <Text style={[styles.initials, { fontSize }]}>{initials}</Text>
      </View>
    );
  };

  if (onPress) {
    return (
      <TouchableOpacity onPress={onPress} style={[styles.container, containerStyle]}>
        {renderContent()}
      </TouchableOpacity>
    );
  }

  return (
    <View style={[styles.container, containerStyle]}>
      {renderContent()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    overflow: 'hidden',
    backgroundColor: '#E5E7EB',
  },
  image: {
    width: '100%',
    height: '100%',
  },
  initialsContainer: {
    width: '100%',
    height: '100%',
    alignItems: 'center',
    justifyContent: 'center',
  },
  initials: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
});

export default Avatar;

