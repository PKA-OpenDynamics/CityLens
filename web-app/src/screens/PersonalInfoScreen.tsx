// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { authService, User } from '../services/auth';
import Avatar from '../components/Avatar';

const PersonalInfoScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
  });
  const [errors, setErrors] = useState<{
    full_name?: string;
    email?: string;
    phone?: string;
  }>({});
  const [touched, setTouched] = useState<{
    full_name?: boolean;
    email?: boolean;
    phone?: boolean;
  }>({});

  useEffect(() => {
    loadUserInfo();
  }, []);

  const loadUserInfo = async () => {
    try {
      const userData = await authService.getCurrentUser();
      setUser(userData);
      setFormData({
        full_name: userData.full_name || '',
        email: userData.email || '',
        phone: userData.phone || '',
      });
    } catch (error: any) {
      Alert.alert('Lỗi', 'Không thể tải thông tin người dùng');
      navigation.goBack();
    } finally {
      setLoading(false);
    }
  };

  // Validation functions
  const validateFullName = (name: string): boolean => {
    return name.trim().length >= 2;
  };

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePhone = (phone: string): boolean => {
    if (!phone.trim()) return true; // Optional field
    // Vietnamese phone number format: 10-11 digits, may start with 0 or +84
    const phoneRegex = /^(\+84|0)[0-9]{9,10}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
  };

  const validateField = (field: string, value: string) => {
    const newErrors = { ...errors };

    if (field === 'full_name') {
      if (!value.trim()) {
        newErrors.full_name = 'Vui lòng nhập họ và tên';
      } else if (!validateFullName(value)) {
        newErrors.full_name = 'Họ và tên phải có ít nhất 2 ký tự';
      } else {
        delete newErrors.full_name;
      }
    } else if (field === 'email') {
      if (!value.trim()) {
        newErrors.email = 'Vui lòng nhập email';
      } else if (!validateEmail(value)) {
        newErrors.email = 'Email không hợp lệ';
      } else {
        delete newErrors.email;
      }
    } else if (field === 'phone') {
      if (value.trim() && !validatePhone(value)) {
        newErrors.phone = 'Số điện thoại không hợp lệ (VD: 0912345678 hoặc +84912345678)';
      } else {
        delete newErrors.phone;
      }
    }

    setErrors(newErrors);
  };

  const handleFieldChange = (field: 'full_name' | 'email' | 'phone', value: string) => {
    setFormData({ ...formData, [field]: value });
    if (touched[field]) {
      validateField(field, value);
    }
  };

  const handleBlur = (field: 'full_name' | 'email' | 'phone') => {
    setTouched({ ...touched, [field]: true });
    validateField(field, formData[field]);
  };

  const isFormValid = (): boolean => {
    return (
      validateFullName(formData.full_name) &&
      validateEmail(formData.email) &&
      (!formData.phone || validatePhone(formData.phone))
    );
  };

  const handleSave = async () => {
    // Mark all fields as touched
    setTouched({
      full_name: true,
      email: true,
      phone: true,
    });

    // Validate all fields
    validateField('full_name', formData.full_name);
    validateField('email', formData.email);
    validateField('phone', formData.phone);

    if (!isFormValid()) {
      return;
    }

    // TODO: Implement update user API call
    setSaving(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      Alert.alert('Thành công', 'Đã cập nhật thông tin cá nhân');
    } catch (error: any) {
      Alert.alert('Lỗi', error.message || 'Không thể cập nhật thông tin');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#20A957" />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <LinearGradient
        colors={['#20A957', '#7BE882']}
        style={styles.header}
      >
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
        >
          <MaterialIcons name="arrow-back" size={24} color="#FFFFFF" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Thông tin cá nhân</Text>
      </LinearGradient>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        <View style={styles.avatarSection}>
          <Avatar size={80} />
          <TouchableOpacity style={styles.changeAvatarButton}>
            <Text style={styles.changeAvatarText}>Đổi ảnh đại diện</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.form}>
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Họ và tên</Text>
            <View style={[styles.inputContainer, errors.full_name && styles.inputError]}>
              <MaterialIcons name="person" size={20} color="#9CA3AF" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                value={formData.full_name}
                onChangeText={(text) => handleFieldChange('full_name', text)}
                onBlur={() => handleBlur('full_name')}
                placeholder="Họ và tên"
              />
            </View>
            {errors.full_name && touched.full_name && (
              <Text style={styles.errorText}>{errors.full_name}</Text>
            )}
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Email</Text>
            <View style={[styles.inputContainer, errors.email && styles.inputError]}>
              <MaterialIcons name="email" size={20} color="#9CA3AF" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                value={formData.email}
                onChangeText={(text) => handleFieldChange('email', text)}
                onBlur={() => handleBlur('email')}
                placeholder="Email"
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>
            {errors.email && touched.email && (
              <Text style={styles.errorText}>{errors.email}</Text>
            )}
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Số điện thoại</Text>
            <View style={[styles.inputContainer, errors.phone && styles.inputError]}>
              <MaterialIcons name="phone" size={20} color="#9CA3AF" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                value={formData.phone}
                onChangeText={(text) => handleFieldChange('phone', text)}
                onBlur={() => handleBlur('phone')}
                placeholder="Số điện thoại"
                keyboardType="phone-pad"
              />
            </View>
            {errors.phone && touched.phone && (
              <Text style={styles.errorText}>{errors.phone}</Text>
            )}
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Tên đăng nhập</Text>
            <View style={[styles.inputContainer, styles.inputDisabled]}>
              <MaterialIcons name="account-circle" size={20} color="#9CA3AF" style={styles.inputIcon} />
              <Text style={styles.inputDisabledText}>{user?.username}</Text>
            </View>
            <Text style={styles.helperText}>Tên đăng nhập không thể thay đổi</Text>
          </View>

          <TouchableOpacity
            style={[
              styles.saveButton,
              (saving || !isFormValid()) && styles.saveButtonDisabled
            ]}
            onPress={handleSave}
            disabled={saving || !isFormValid()}
          >
            {saving ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <Text style={styles.saveButtonText}>Lưu thay đổi</Text>
            )}
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    paddingTop: 16,
    paddingBottom: 24,
    paddingHorizontal: 16,
  },
  backButton: {
    alignSelf: 'flex-start',
    marginBottom: 16,
    padding: 8,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: 24,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarSection: {
    alignItems: 'center',
    marginBottom: 32,
  },
  changeAvatarButton: {
    marginTop: 16,
  },
  changeAvatarText: {
    color: '#20A957',
    fontSize: 14,
    fontWeight: '600',
  },
  form: {
    width: '100%',
  },
  inputGroup: {
    marginBottom: 24,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 16,
    height: 52,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  inputError: {
    borderColor: '#EF4444',
  },
  inputDisabled: {
    backgroundColor: '#F3F4F6',
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: '#111827',
  },
  inputDisabledText: {
    flex: 1,
    fontSize: 16,
    color: '#9CA3AF',
  },
  helperText: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  saveButton: {
    backgroundColor: '#20A957',
    borderRadius: 12,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  errorText: {
    color: '#EF4444',
    fontSize: 12,
    marginTop: 4,
    marginLeft: 4,
  },
});

export default PersonalInfoScreen;


