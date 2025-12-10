// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
  Alert,
  PermissionsAndroid,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { aiChatService, ChatMessage as AIChatMessage, ChatHistoryItem } from '../services/aiChat';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/auth';

// Ngã Tư Sở - Quận Thanh Xuân, Hà Nội
const DEFAULT_LOCATION = {
  latitude: 21.003204,
  longitude: 105.819673,
};

type ChatMessage = {
  id: string;
  text: string;
  isUser: boolean;
};

/**
 * AiAssistantScreen.native
 * Chat với AI CityLens sử dụng Google Gemini
 * Tích hợp với TomTom, OpenWeatherMap và database
 */

const AiAssistantScreen: React.FC = () => {

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [userLocation] = useState<{ latitude: number; longitude: number }>(DEFAULT_LOCATION);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const navigation = useNavigation<any>();
  const { user, isAuthenticated } = useAuth();
  const recognitionRef = useRef<any | null>(null);

  // Cleanup voice recognition on unmount
  useEffect(() => {
    return () => {
      stopVoiceInput();
    };
  }, []);

  // Fetch chat history when screen mounts
  useEffect(() => {
    const fetchHistory = async () => {
      setLoadingHistory(true);
      try {
        let token: string | undefined;
        if (isAuthenticated) {
          try {
            const storedToken = await authService.getToken();
            token = storedToken || undefined;
          } catch {}
        }

        const userId = user?.id || user?._id;
        const res = await aiChatService.getHistory(
          { limit: 30, skip: 0, userId },
          token
        );
        console.log('[AI Chat] History fetch:', res);
        if (res.success && res.data) {
          // reverse to oldest -> newest for display append order
          const history = (res.data as ChatHistoryItem[]).slice().reverse();
          const mapped = history.flatMap<ChatMessage>((item) => {
            const items: ChatMessage[] = [];
            if (item.message) {
              items.push({
                id: `${item._id}-q`,
                text: item.message,
                isUser: true,
              });
            }
            if (item.response) {
              items.push({
                id: `${item._id}-a`,
                text: item.response,
                isUser: false,
              });
            }
            return items;
          });
          setMessages(mapped);
        }
      } catch (err) {
        console.warn('[AI Chat] Failed to load history:', err);
      } finally {
        setLoadingHistory(false);
      }
    };

    fetchHistory();
  }, [isAuthenticated, user]);

  const appendMessage = (msg: Omit<ChatMessage, 'id'>) => {
    setMessages((prev) => [
      ...prev,
      { ...msg, id: `${Date.now()}-${Math.random()}` },
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
        const nextText = input ? `${input.trim()} ${transcript.trim()}` : transcript.trim();
        setInput(nextText);
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

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isSending) return;
    setIsSending(true);
    appendMessage({ text, isUser: true });
    setInput('');

    try {
      // Get auth token if available
      let token: string | undefined;
      if (isAuthenticated) {
        try {
          const storedToken = await authService.getToken();
          token = storedToken || undefined;
        } catch (e) {
          // Token not available, continue without it
        }
      }

      // Build conversation history
      const conversationHistory: AIChatMessage[] = messages
        .slice(-10) // Last 10 messages
        .map((msg) => ({
          role: msg.isUser ? 'user' : 'assistant',
          content: msg.text,
        }));

      // Call AI chat API
      const response = await aiChatService.chat(
        {
          message: text,
          conversation_history: conversationHistory,
          user_location: userLocation,
          user_id: user?.id || user?._id,
        },
        token
      );

      if (response.success && response.data) {
        appendMessage({ text: response.data.response, isUser: false });
      } else {
        appendMessage({
          text: response.error || 'Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi của bạn.',
          isUser: false,
        });
      }
    } catch (error: any) {
      console.error('Error chatting with AI:', error);
      appendMessage({
        text: 'Xin lỗi, đã xảy ra lỗi khi kết nối với AI. Vui lòng thử lại sau.',
        isUser: false,
      });
    } finally {
      setIsSending(false);
    }
  };

  const renderItem = ({ item }: { item: ChatMessage }) => (
    <ChatBubble message={item} />
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        style={styles.root}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 80 : 0}
      >
        <View style={styles.header}>
          <TouchableOpacity
            onPress={() => navigation.goBack()}
            style={styles.backButton}
          >
            <MaterialIcons name="arrow-back" size={24} color="#20A957" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Chat với AI CityLens</Text>
        </View>

        <View style={styles.chatContainer}>
          <FlatList
            data={[...messages].reverse()}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <ChatBubble message={item} />
            )}
            contentContainerStyle={styles.chatList}
            inverted
          />
          {isSending && (
            <View style={styles.typingRow}>
              <View style={styles.typingDot} />
              <Text style={styles.typingText}>AI đang trả lời...</Text>
            </View>
          )}
        </View>

        <View style={styles.inputWrapper}>
          <TouchableOpacity
            style={[styles.voiceButton, isRecording && styles.voiceButtonActive]}
            onPress={handleVoiceInput}
            disabled={isSending}
          >
            <MaterialIcons
              name={isRecording ? "mic" : "mic-none"}
              size={20}
              color={isRecording ? "#EF4444" : "#6B7280"}
            />
          </TouchableOpacity>
          <TextInput
            style={styles.input}
            value={input}
            onChangeText={setInput}
            placeholder="Hỏi AI về ngập, tắc đường, dịch vụ gần bạn..."
            multiline
            onSubmitEditing={() => handleSend()}
          />
          {isRecording ? (
            <TouchableOpacity
              style={styles.stopButton}
              onPress={stopVoiceInput}
            >
              <MaterialIcons
                name="stop"
                size={20}
                color="#FFFFFF"
              />
            </TouchableOpacity>
          ) : (
          <TouchableOpacity
            style={styles.sendButton}
            onPress={handleSend}
            disabled={isSending || !input.trim()}
          >
            <MaterialIcons
              name="send"
              size={20}
              color="#FFFFFF"
            />
          </TouchableOpacity>
          )}
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

type ChatBubbleProps = {
  message: ChatMessage;
};

const ChatBubble: React.FC<ChatBubbleProps> = ({ message }) => {
  const align = message.isUser ? 'flex-end' : 'flex-start';
  const bgColor = message.isUser ? '#20A957' : '#FFFFFF';
  const textColor = message.isUser ? '#FFFFFF' : '#111827';

  return (
    <View style={[styles.bubbleRow, { justifyContent: align }]}>
      <View
        style={[
          styles.bubble,
          {
            backgroundColor: bgColor,
            borderBottomLeftRadius: message.isUser ? 16 : 4,
            borderBottomRightRadius: message.isUser ? 4 : 16,
          },
        ]}
      >
        <Text style={[styles.bubbleText, { color: textColor }]}>
          {message.text}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  root: {
    flex: 1,
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
  chatContainer: {
    flex: 1,
    backgroundColor: '#F5F5F7',
  },
  chatList: {
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  bubbleRow: {
    flexDirection: 'row',
    marginVertical: 4,
  },
  bubble: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    maxWidth: '75%',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
    elevation: 1,
  },
  bubbleText: {
    fontSize: 14,
  },
  typingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingBottom: 4,
  },
  typingDot: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: '#D1D5DB',
    marginRight: 8,
  },
  typingText: {
    fontSize: 12,
    color: '#6B7280',
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 8,
    paddingVertical: 8,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#E5E7EB',
    backgroundColor: '#FFFFFF',
  },
  voiceButton: {
    marginRight: 8,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#F3F4F6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  voiceButtonActive: {
    backgroundColor: '#FEE2E2',
    borderWidth: 1,
    borderColor: '#FCA5A5',
  },
  input: {
    flex: 1,
    maxHeight: 100,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 14,
  },
  sendButton: {
    marginLeft: 8,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#20A957',
    alignItems: 'center',
    justifyContent: 'center',
  },
  stopButton: {
    marginLeft: 8,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#EF4444',
    alignItems: 'center',
    justifyContent: 'center',
  },
});

export default AiAssistantScreen;


