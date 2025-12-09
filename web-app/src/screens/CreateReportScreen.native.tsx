// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  Modal,
  FlatList,
  Image,
  PermissionsAndroid,
  Platform,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import * as ImagePicker from 'expo-image-picker';
import reportsService from '../services/reports';

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
  const [addressDetail, setAddressDetail] = useState('');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [images, setImages] = useState<Array<{ uri: string; type: 'image' | 'video' }>>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showTypeModal, setShowTypeModal] = useState(false);
  const [showWardModal, setShowWardModal] = useState(false);
  const [showMapModal, setShowMapModal] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const mapModalRef = useRef<any>(null);
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const markerRef = useRef<any>(null);
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

  const validateImages = (mediaList: Array<{ uri: string; type: 'image' | 'video' }>): boolean => {
    return mediaList.length >= 1 && mediaList.length <= 5;
  };

  const recognitionRef = useRef<any | null>(null);

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
      Alert.alert('Lỗi', 'Cần quyền truy cập thư viện ảnh/video');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images', 'videos'],
      allowsMultipleSelection: true,
      quality: 0.8,
    });

    if (!result.canceled && result.assets) {
      const newMedia = result.assets.map((asset) => ({
        uri: asset.uri,
        type: asset.type === 'video' ? 'video' as const : 'image' as const,
      }));
      const updatedImages = [...images, ...newMedia].slice(0, 5); // Tối đa 5 ảnh/video
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

  const stopVoiceInput = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (err) {
        // ignore stop errors
      }
      recognitionRef.current = null;
    }
    setIsRecording(false);
  };

  const handleVoiceInput = async () => {
    // Toggle off if already recording
    if (isRecording) {
      stopVoiceInput();
      return;
    }

    // Native platforms: best-effort permission prompt, but speech recognition is web-only in this mock.
    if (Platform.OS === 'android') {
      const granted = await PermissionsAndroid.request(
        PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
        {
          title: 'Cấp quyền micro',
          message: 'Ứng dụng cần quyền micro để ghi âm và chuyển thành văn bản.',
          buttonPositive: 'Đồng ý',
          buttonNegative: 'Từ chối',
        }
      );

      if (granted !== PermissionsAndroid.RESULTS.GRANTED) {
        Alert.alert('Thông báo', 'Bạn cần cấp quyền micro để sử dụng tính năng này.');
        return;
      }
    }

    // Web speech recognition
    if (typeof window === 'undefined') {
      Alert.alert('Thông báo', 'Trình duyệt không hỗ trợ nhập giọng nói.');
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      Alert.alert('Thông báo', 'Trình duyệt không hỗ trợ Web Speech API.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'vi-VN';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event: any) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        if (event.results[i].isFinal) {
          transcript += event.results[i][0].transcript;
        }
      }

      if (transcript) {
        const nextText = content ? `${content.trim()} ${transcript.trim()}` : transcript.trim();
        setContent(nextText);
        if (!touched.content) {
          setTouched({ ...touched, content: true });
        }
        validateField('content', nextText);
      }
    };

    recognition.onerror = () => {
      stopVoiceInput();
      Alert.alert('Lỗi', 'Không thể nhận dạng giọng nói. Vui lòng thử lại.');
    };

    recognition.onend = () => {
      stopVoiceInput();
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
      setIsRecording(true);
    } catch (err) {
      recognitionRef.current = null;
      Alert.alert('Lỗi', 'Không thể khởi động thu âm. Vui lòng thử lại.');
    }
  };

  useEffect(() => {
    return () => {
      stopVoiceInput();
    };
  }, []);

  // Get user's current location when modal opens
  useEffect(() => {
    if (showMapModal && typeof window !== 'undefined') {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            setUserLocation({
              lat: position.coords.latitude,
              lng: position.coords.longitude,
            });
          },
          (error) => {
            // Use default location (Hoan Kiem Lake) if geolocation fails
            setUserLocation({
              lat: 21.0285,
              lng: 105.8542,
            });
          },
          {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0,
          }
        );
      } else {
        // If geolocation is not available, use default location
        setUserLocation({
          lat: 21.0285,
          lng: 105.8542,
        });
      }
    } else {
      // Reset userLocation when modal closes
      setUserLocation(null);
    }
  }, [showMapModal]);

  // Initialize map when modal opens and userLocation is ready
  useEffect(() => {
    if (showMapModal && userLocation && typeof window !== 'undefined') {
      const loadLeaflet = async () => {
        // Load CSS if not already loaded
        if (!document.getElementById('leaflet-css')) {
          const link = document.createElement('link');
          link.id = 'leaflet-css';
          link.rel = 'stylesheet';
          link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
          document.head.appendChild(link);
        }

        // Load JS if not already loaded
        if (!(window as any).L) {
          const script = document.createElement('script');
          script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
          script.onload = () => {
            initializeMap();
          };
          document.body.appendChild(script);
        } else {
          // Clean up existing map if any
          if (mapModalRef.current) {
            mapModalRef.current.remove();
            mapModalRef.current = null;
          }
          initializeMap();
        }
      };

      loadLeaflet();
    }

    return () => {
      // Cleanup map when modal closes
      if (!showMapModal && mapModalRef.current) {
        mapModalRef.current.remove();
        mapModalRef.current = null;
        markerRef.current = null;
      }
    };
  }, [showMapModal, userLocation]);

  const initializeMap = () => {
    if (!mapContainerRef.current || !(window as any).L) return;

    const L = (window as any).L;
    
    // Priority: selectedLocation > userLocation > default (Hoan Kiem Lake)
    const defaultCenter: [number, number] = selectedLocation 
      ? [selectedLocation.lat, selectedLocation.lng]
      : userLocation
      ? [userLocation.lat, userLocation.lng]
      : [21.0285, 105.8542]; // Hồ Hoàn Kiếm

    // Initialize map
    mapModalRef.current = L.map(mapContainerRef.current, {
      center: defaultCenter,
      zoom: 15,
      zoomControl: true,
    });

    // Add satellite tile layer (Esri World Imagery)
    L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      {
        maxZoom: 19,
        attribution:
          'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
      }
    ).addTo(mapModalRef.current);

    // Update location when map is moved (marker is fixed at center visually)
    const updateLocationFromCenter = () => {
      const center = mapModalRef.current.getCenter();
      setSelectedLocation({ lat: center.lat, lng: center.lng });
    };

    mapModalRef.current.on('moveend', updateLocationFromCenter);
    mapModalRef.current.on('dragend', updateLocationFromCenter);

    // Set initial location
    setSelectedLocation({ lat: defaultCenter[0], lng: defaultCenter[1] });
  };

  const handleSaveLocation = () => {
    if (selectedLocation) {
      // Location is already saved in state
      setShowMapModal(false);
    }
  };

  const handleCancelMap = () => {
    setShowMapModal(false);
    // Optionally reset location if user cancels
    // setSelectedLocation(null);
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

  const handleSubmit = async () => {
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

    // Prevent double submission
    if (isSubmitting) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Prepare media files
      const preparedMedia = await reportsService.prepareMediaFiles(images);

      // Create report data
      const reportData = {
        reportType: reportType!,
        ward: ward!,
        addressDetail: addressDetail || undefined,
        location: selectedLocation || undefined,
        title: title || undefined,
        content: content,
        media: preparedMedia,
      };

      // Submit report
      const response = await reportsService.createReport(reportData);

      if (response.success && response.data) {
        // Reset form
        setReportType(null);
        setWard(null);
        setAddressDetail('');
        setTitle('');
        setContent('');
        setImages([]);
        setSelectedLocation(null);
        setTouched({});
        setIsSubmitting(false);
        
        // Navigate to ReportHome and show success message
        navigation.navigate('ReportHome', {
          showSuccessMessage: true,
          message: 'Tạo phản ánh thành công'
        });
      } else {
        throw new Error(response.error || 'Failed to create report');
      }
    } catch (error: any) {
      
      let errorMessage = 'Không thể gửi báo cáo. Vui lòng thử lại sau.';
      
      if (error.message) {
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
          errorMessage = 'Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng và đảm bảo backend server đang chạy.';
        } else {
          errorMessage = error.message;
        }
      }

      Alert.alert('Lỗi', errorMessage, [{ text: 'OK' }]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderDropdownModal = (
    visible: boolean,
    onClose: () => void,
    items: string[],
    selected: string | null,
    onSelect: (item: string) => void,
    title: string
  ) => (
    <Modal 
      visible={visible} 
      transparent 
      animationType="slide"
      accessibilityViewIsModal={true}
      onRequestClose={onClose}
    >
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
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
        >
          <MaterialIcons name="arrow-back" size={24} color="#20A957" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Gửi phản ánh</Text>
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        <View style={styles.form}>
          <Text style={styles.label}>
            Loại phản ánh <Text style={styles.requiredStar}>*</Text>
          </Text>
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

          <Text style={styles.label}>
            Địa điểm <Text style={styles.requiredStar}>*</Text>
          </Text>
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

          <TextInput
            style={styles.input}
            placeholder="Số nhà, thôn/xóm, khu vực "
            value={addressDetail}
            onChangeText={setAddressDetail}
          />

          <TouchableOpacity
            style={styles.mapButton}
            onPress={() => setShowMapModal(true)}
          >
            <MaterialIcons name="place" size={20} color="#20A957" />
            <Text style={styles.mapButtonText}>Chọn địa điểm từ bản đồ</Text>
          </TouchableOpacity>
          {selectedLocation && (
            <Text style={styles.selectedLocationText}>
              Đã chọn: {selectedLocation.lat.toFixed(6)}, {selectedLocation.lng.toFixed(6)}
            </Text>
          )}

          <Text style={styles.label}>Tiêu đề</Text>
          <TextInput
            style={styles.input}
            placeholder="Nhập tiêu đề phản ánh"
            value={title}
            onChangeText={setTitle}
          />

          <Text style={styles.label}>
            Nội dung <Text style={styles.requiredStar}>*</Text>
          </Text>
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

          <TouchableOpacity
            style={[styles.voiceButton, isRecording && styles.voiceButtonActive]}
            onPress={handleVoiceInput}
          >
            <MaterialIcons
              name={isRecording ? 'stop' : 'mic'}
              size={20}
              color={isRecording ? '#DC2626' : '#20A957'}
            />
            <Text style={styles.voiceButtonText}>
              {isRecording ? 'Dừng nhập giọng nói' : 'Ấn để nhập nội dung bằng giọng nói'}
            </Text>
          </TouchableOpacity>

          <Text style={styles.label}>
            Ảnh/Video <Text style={styles.requiredStar}>*</Text>
          </Text>
          <Text style={styles.helperText}>
            Cho phép tổng dung lượng tối đa 30MB (tối thiểu 1, tối đa 5 ảnh/video)
          </Text>
          {errors.images && touched.images && (
            <Text style={styles.errorText}>{errors.images}</Text>
          )}
          <View style={styles.imageContainer}>
            {images.map((media, index) => (
              <View key={index} style={styles.imageWrapper}>
                {media.type === 'video' ? (
                  <View style={styles.videoPreview}>
                    <MaterialIcons name="videocam" size={32} color="#FFFFFF" />
                    <View style={styles.videoBadge}>
                      <MaterialIcons name="play-circle-filled" size={20} color="#FFFFFF" />
                    </View>
                  </View>
                ) : (
                  <Image source={{ uri: media.uri }} style={styles.imagePreview} />
                )}
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

          <View style={styles.buttonRow}>
            <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
              <Text style={styles.saveButtonText}>Lưu lại</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.submitButton,
                (!isFormValid() || isSubmitting) && styles.submitButtonDisabled,
              ]}
              onPress={handleSubmit}
              disabled={isSubmitting}
              activeOpacity={0.7}
            >
              {isSubmitting ? (
                <View style={styles.submitButtonLoading}>
                  <ActivityIndicator size="small" color="#20A957" style={{ marginRight: 8 }} />
                  <Text style={styles.submitButtonText}>Đang gửi...</Text>
                </View>
              ) : (
                <Text style={styles.submitButtonText}>
                  {!isFormValid() ? 'Vui lòng điền đầy đủ thông tin' : 'Gửi phản ánh'}
                </Text>
              )}
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

      {/* Map Selection Modal */}
      <Modal 
        visible={showMapModal} 
        transparent 
        animationType="slide"
        accessibilityViewIsModal={true}
        onRequestClose={handleCancelMap}
      >
        <View style={styles.mapModalOverlay}>
          <View style={styles.mapModalContent}>
            <View style={styles.mapModalHeader}>
              <Text style={styles.mapModalTitle}>Chọn địa điểm trên bản đồ</Text>
              <TouchableOpacity onPress={handleCancelMap}>
                <MaterialIcons name="close" size={24} color="#111827" />
              </TouchableOpacity>
            </View>
            <View style={styles.mapContainer}>
              <div
                ref={mapContainerRef}
                style={{
                  width: '100%',
                  height: '100%',
                  zIndex: 1,
                }}
              />
              {/* Fixed marker icon at center */}
              <View style={styles.centerMarker}>
                <View style={styles.markerIcon}>
                  <MaterialIcons name="place" size={32} color="#20A957" />
                </View>
              </View>
            </View>
            <View style={styles.mapModalFooter}>
              <TouchableOpacity
                style={styles.mapCancelButton}
                onPress={handleCancelMap}
              >
                <Text style={styles.mapCancelButtonText}>Hủy</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.mapSaveButton, !selectedLocation && styles.mapSaveButtonDisabled]}
                onPress={handleSaveLocation}
                disabled={!selectedLocation}
              >
                <Text style={styles.mapSaveButtonText}>Lưu</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    backgroundColor: '#FFFFFF',
    paddingTop: 16,
    paddingBottom: 24,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  backButton: {
    position: 'absolute',
    left: 16,
    padding: 8,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#20A957',
    textAlign: 'center',
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
  requiredStar: {
    color: '#EF4444',
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
    color: '#20A957',
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
  voiceButtonActive: {
    backgroundColor: '#FEE2E2',
    borderWidth: 1,
    borderColor: '#FCA5A5',
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
  videoPreview: {
    width: '100%',
    height: '100%',
    borderRadius: 8,
    backgroundColor: '#1F2937',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  videoBadge: {
    position: 'absolute',
    bottom: 8,
    right: 8,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    borderRadius: 12,
    padding: 4,
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
    backgroundColor: '#FFFFFF',
    borderWidth: 2,
    borderColor: '#20A957',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    minHeight: 50,
    justifyContent: 'center',
  },
  submitButtonText: {
    color: '#20A957',
    fontSize: 16,
    fontWeight: '700',
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonLoading: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
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
  mapModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  mapModalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    height: Dimensions.get('window').height * 0.67, // 2/3 of screen
    maxHeight: '67%',
  },
  mapModalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  mapModalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  mapContainer: {
    flex: 1,
    width: '100%',
    position: 'relative',
  },
  centerMarker: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    marginTop: -20,
    marginLeft: -20,
    width: 40,
    height: 40,
    zIndex: 1000,
    pointerEvents: 'none',
    alignItems: 'center',
    justifyContent: 'center',
  },
  markerIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFFFFF',
    borderWidth: 3,
    borderColor: '#20A957',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  mapModalFooter: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  mapCancelButton: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  mapCancelButtonText: {
    color: '#374151',
    fontSize: 16,
    fontWeight: '600',
  },
  mapSaveButton: {
    flex: 1,
    backgroundColor: '#20A957',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  mapSaveButtonDisabled: {
    opacity: 0.5,
  },
  mapSaveButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  selectedLocationText: {
    fontSize: 12,
    color: '#20A957',
    marginTop: 8,
    marginBottom: 8,
  },
});

export default CreateReportScreen;
