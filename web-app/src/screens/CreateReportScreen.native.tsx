// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  Switch,
  Modal,
  FlatList,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import * as ImagePicker from 'expo-image-picker';

const REPORT_TYPES = [
  'Ổ gà',
  'Ngập',
  'Rác',
  'Ùn tắc',
  'Đèn giao thông hỏng',
  'Hành vi nguy hiểm',
  'Khác',
];

const WARDS = [
  'Phường Cầu Giấy',
  'Phường Dịch Vọng',
  'Phường Mai Dịch',
  'Phường Nghĩa Đô',
  'Phường Nghĩa Tân',
  'Phường Quan Hoa',
  'Phường Trung Hòa',
  'Phường Yên Hòa',
];

const CreateReportScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const [reportType, setReportType] = useState<string | null>(null);
  const [ward, setWard] = useState<string | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isPublicName, setIsPublicName] = useState(true);
  const [images, setImages] = useState<string[]>([]);
  const [showTypeModal, setShowTypeModal] = useState(false);
  const [showWardModal, setShowWardModal] = useState(false);
  const [errors, setErrors] = useState<{
    reportType?: string;
    ward?: string;
    content?: string;
    images?: string;
  }>({});
  const [touched, setTouched] = useState<{
    reportType?: boolean;
    ward?: boolean;
    content?: boolean;
    images?: boolean;
  }>({});

  // Validation functions
  const validateContent = (content: string): boolean => {
    const trimmed = content.trim();
    return trimmed.length >= 10 && trimmed.length <= 2000;
  };

  const validateImages = (imageList: string[]): boolean => {
    return imageList.length >= 1 && imageList.length <= 5;
  };

  const validateField = (field: string, value: any) => {
    const newErrors = { ...errors };

    if (field === 'reportType') {
      if (!value) {
        newErrors.reportType = 'Vui lòng chọn loại phản ánh';
      } else {
        delete newErrors.reportType;
      }
    } else if (field === 'ward') {
      if (!value) {
        newErrors.ward = 'Vui lòng chọn địa điểm';
      } else {
        delete newErrors.ward;
      }
    } else if (field === 'content') {
      if (!value.trim()) {
        newErrors.content = 'Vui lòng nhập nội dung phản ánh';
      } else if (value.trim().length < 10) {
        newErrors.content = 'Nội dung phải có ít nhất 10 ký tự';
      } else if (value.trim().length > 2000) {
        newErrors.content = 'Nội dung không được vượt quá 2000 ký tự';
      } else {
        delete newErrors.content;
      }
    } else if (field === 'images') {
      if (!validateImages(value)) {
        if (value.length === 0) {
          newErrors.images = 'Vui lòng thêm ít nhất một ảnh/video';
        } else if (value.length > 5) {
          newErrors.images = 'Chỉ được thêm tối đa 5 ảnh/video';
        }
      } else {
        delete newErrors.images;
      }
    }

    setErrors(newErrors);
  };

  const isFormValid = (): boolean => {
    return (
      !!reportType &&
      !!ward &&
      validateContent(content) &&
      validateImages(images)
    );
  };

  const handlePickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Lỗi', 'Cần quyền truy cập thư viện ảnh');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsMultiple: true,
      quality: 0.8,
    });

    if (!result.canceled && result.assets) {
      const newImages = result.assets.map((asset) => asset.uri);
      const updatedImages = [...images, ...newImages].slice(0, 5); // Tối đa 5 ảnh
      setImages(updatedImages);
      if (touched.images) {
        validateField('images', updatedImages);
      }
    }
  };

  const handleRemoveImage = (index: number) => {
    const updatedImages = images.filter((_, i) => i !== index);
    setImages(updatedImages);
    if (touched.images) {
      validateField('images', updatedImages);
    }
  };

  const handleSave = () => {
    // TODO: Lưu bản nháp
    Alert.alert('Thành công', 'Đã lưu bản nháp', [
      { text: 'OK', onPress: () => navigation.goBack() },
    ]);
  };

  const handleReportTypeSelect = (item: string) => {
    setReportType(item);
    setTouched({ ...touched, reportType: true });
    validateField('reportType', item);
  };

  const handleWardSelect = (item: string) => {
    setWard(item);
    setTouched({ ...touched, ward: true });
    validateField('ward', item);
  };

  const handleContentChange = (text: string) => {
    setContent(text);
    if (touched.content) {
      validateField('content', text);
    }
  };

  const handleContentBlur = () => {
    setTouched({ ...touched, content: true });
    validateField('content', content);
  };

  const handleSubmit = () => {
    // Mark all fields as touched
    setTouched({
      reportType: true,
      ward: true,
      content: true,
      images: true,
    });

    // Validate all fields
    validateField('reportType', reportType);
    validateField('ward', ward);
    validateField('content', content);
    validateField('images', images);

    if (!isFormValid()) {
      return;
    }

    // TODO: Gửi báo cáo lên server
    Alert.alert('Thành công', 'Báo cáo đã được gửi', [
      { text: 'OK', onPress: () => navigation.goBack() },
    ]);
  };

  const renderDropdownModal = (
    visible: boolean,
    onClose: () => void,
    items: string[],
    selected: string | null,
    onSelect: (item: string) => void,
    title: string
  ) => (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.modalOverlay}>
        <View style={styles.modalContent}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>{title}</Text>
            <TouchableOpacity onPress={onClose}>
              <MaterialIcons name="close" size={24} color="#111827" />
            </TouchableOpacity>
          </View>
          <FlatList
            data={items}
            keyExtractor={(item) => item}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.modalItem}
                onPress={() => {
                  onSelect(item);
                  onClose();
                }}
              >
                <Text style={styles.modalItemText}>{item}</Text>
                {selected === item && (
                  <MaterialIcons name="check" size={20} color="#20A957" />
                )}
              </TouchableOpacity>
            )}
          />
        </View>
      </View>
    </Modal>
  );

  return (
    <SafeAreaView style={styles.container}>
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
        <Text style={styles.headerTitle}>Gửi phản ánh</Text>
      </LinearGradient>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        <View style={styles.form}>
          <Text style={styles.label}>Loại phản ánh *</Text>
              <TouchableOpacity
                style={[styles.dropdown, errors.reportType && styles.inputError]}
                onPress={() => setShowTypeModal(true)}
              >
                <Text style={[styles.dropdownText, !reportType && styles.dropdownPlaceholder]}>
                  {reportType || 'Chọn loại phản ánh (mock)'}
                </Text>
                <MaterialIcons name="arrow-drop-down" size={24} color="#9CA3AF" />
              </TouchableOpacity>
              {errors.reportType && touched.reportType && (
                <Text style={styles.errorText}>{errors.reportType}</Text>
              )}

          <Text style={styles.label}>Địa điểm *</Text>
          <TouchableOpacity
            style={[styles.dropdown, errors.ward && styles.inputError]}
            onPress={() => setShowWardModal(true)}
          >
            <Text style={[styles.dropdownText, !ward && styles.dropdownPlaceholder]}>
              {ward || 'Chọn xã/phường (mock)'}
            </Text>
            <MaterialIcons name="arrow-drop-down" size={24} color="#9CA3AF" />
          </TouchableOpacity>
          {errors.ward && touched.ward && (
            <Text style={styles.errorText}>{errors.ward}</Text>
          )}

          <TouchableOpacity
            style={styles.mapButton}
            onPress={() => navigation.navigate('Map', { selectLocation: true })}
          >
            <MaterialIcons name="place" size={20} color="#3B82F6" />
            <Text style={styles.mapButtonText}>Chọn địa điểm từ bản đồ</Text>
          </TouchableOpacity>

          <Text style={styles.label}>Tiêu đề</Text>
          <TextInput
            style={styles.input}
            placeholder="Nhập tiêu đề phản ánh"
            value={title}
            onChangeText={setTitle}
          />

          <Text style={styles.label}>Nội dung *</Text>
          <TextInput
            style={[styles.input, styles.textArea, errors.content && styles.inputError]}
            placeholder="Mô tả chi tiết nội dung phản ánh (tối thiểu 10 ký tự)"
            value={content}
            onChangeText={handleContentChange}
            onBlur={handleContentBlur}
            multiline
            numberOfLines={6}
            textAlignVertical="top"
            maxLength={2000}
          />
          <Text style={styles.helperText}>
            {content.length}/2000 ký tự {content.length < 10 && touched.content && (
              <Text style={styles.errorText}> - Tối thiểu 10 ký tự</Text>
            )}
          </Text>
          {errors.content && touched.content && (
            <Text style={styles.errorText}>{errors.content}</Text>
          )}

          <TouchableOpacity style={styles.voiceButton}>
            <MaterialIcons name="mic" size={20} color="#3B82F6" />
            <Text style={styles.voiceButtonText}>
              Ấn để nhập nội dung bằng giọng nói (mock)
            </Text>
          </TouchableOpacity>

          <Text style={styles.label}>Ảnh/Video *</Text>
          <Text style={styles.helperText}>
            Cho phép tổng dung lượng tối đa 30MB (tối thiểu 1, tối đa 5 ảnh)
          </Text>
          {errors.images && touched.images && (
            <Text style={styles.errorText}>{errors.images}</Text>
          )}
          <View style={styles.imageContainer}>
            {images.map((uri, index) => (
              <View key={index} style={styles.imageWrapper}>
                <Image source={{ uri }} style={styles.imagePreview} />
                <TouchableOpacity
                  style={styles.removeImageButton}
                  onPress={() => handleRemoveImage(index)}
                >
                  <MaterialIcons name="close" size={16} color="#FFFFFF" />
                </TouchableOpacity>
              </View>
            ))}
            {images.length < 5 && (
              <TouchableOpacity
                style={styles.addImageButton}
                onPress={() => {
                  handlePickImage();
                  setTouched({ ...touched, images: true });
                }}
              >
                <MaterialIcons name="camera-alt" size={28} color="#9CA3AF" />
                <Text style={styles.addImageText}>Thêm{'\n'}Ảnh/Video</Text>
              </TouchableOpacity>
            )}
          </View>

          <View style={styles.switchContainer}>
            <Switch
              value={isPublicName}
              onValueChange={setIsPublicName}
              trackColor={{ false: '#D1D5DB', true: '#20A957' }}
              thumbColor="#FFFFFF"
            />
            <Text style={styles.switchLabel}>Công khai tên người phản ánh</Text>
          </View>

          <View style={styles.buttonRow}>
            <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
              <Text style={styles.saveButtonText}>Lưu lại</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.submitButton, !isFormValid() && styles.submitButtonDisabled]}
              onPress={handleSubmit}
              disabled={!isFormValid()}
            >
              <Text style={styles.submitButtonText}>Gửi phản ánh</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>

      {renderDropdownModal(
        showTypeModal,
        () => setShowTypeModal(false),
        REPORT_TYPES,
        reportType,
        handleReportTypeSelect,
        'Chọn loại phản ánh'
      )}

      {renderDropdownModal(
        showWardModal,
        () => setShowWardModal(false),
        WARDS,
        ward,
        handleWardSelect,
        'Chọn xã/phường'
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
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
    padding: 16,
  },
  form: {
    width: '100%',
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
    marginTop: 16,
  },
  dropdown: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  inputError: {
    borderColor: '#EF4444',
  },
  dropdownText: {
    flex: 1,
    fontSize: 16,
    color: '#111827',
  },
  dropdownPlaceholder: {
    color: '#9CA3AF',
  },
  mapButton: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    marginBottom: 8,
  },
  mapButtonText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#3B82F6',
  },
  input: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#111827',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  textArea: {
    height: 120,
    paddingTop: 16,
  },
  voiceButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
    borderRadius: 8,
    padding: 12,
    marginTop: 8,
  },
  voiceButtonText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#374151',
  },
  helperText: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 8,
  },
  imageContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  imageWrapper: {
    width: 120,
    height: 120,
    marginRight: 8,
    marginBottom: 8,
    position: 'relative',
  },
  imagePreview: {
    width: '100%',
    height: '100%',
    borderRadius: 8,
  },
  removeImageButton: {
    position: 'absolute',
    top: 4,
    right: 4,
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#EF4444',
    alignItems: 'center',
    justifyContent: 'center',
  },
  addImageButton: {
    width: 120,
    height: 120,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderStyle: 'dashed',
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  addImageText: {
    marginTop: 8,
    fontSize: 12,
    color: '#9CA3AF',
    textAlign: 'center',
  },
  switchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 16,
    marginBottom: 24,
  },
  switchLabel: {
    marginLeft: 12,
    fontSize: 14,
    color: '#374151',
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 12,
  },
  saveButton: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  saveButtonText: {
    color: '#374151',
    fontSize: 16,
    fontWeight: '600',
  },
  submitButton: {
    flex: 1,
    backgroundColor: '#20A957',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  errorText: {
    color: '#EF4444',
    fontSize: 12,
    marginTop: 4,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '70%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  modalItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  modalItemText: {
    fontSize: 16,
    color: '#111827',
  },
});

export default CreateReportScreen;
