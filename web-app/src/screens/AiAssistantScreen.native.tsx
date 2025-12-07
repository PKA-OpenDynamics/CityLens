// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';

type ChatMessage = {
  id: string;
  text: string;
  isUser: boolean;
};

/**
 * AiAssistantScreen.native
 * Chat đơn giản port từ `AIAssistantScreen` Flutter:
 * - Lưu lịch sử message trong state.
 * - Trả lời bằng rule-based dummy giống Flutter.
 */

const AiAssistantScreen: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const navigation = useNavigation<any>();

  const generateDummyAnswer = (question: string): string => {
    const q = question.toLowerCase();
    if (q.includes('ngập')) {
      return 'Đoạn đường từ Hà Đông đến Ba Đình hiện có một số điểm ngập nhẹ vào giờ cao điểm.';
    }
    if (q.includes('camera')) {
      return 'Camera gần nhất ở ngã tư Cầu Giấy, cách bạn khoảng 500m.';
    }
    if (q.includes('quán ăn')) {
      return 'Gợi ý quán ăn đang mở gần bạn: Quán Bún Chả Hương Liên, Nhà hàng Phở Thìn.';
    }
    if (q.includes('tắc')) {
      return 'Đường X hôm nay có tắc nhẹ vào buổi chiều.';
    }
    if (q.includes('trú mưa')) {
      return 'Hiện tại có điểm trú mưa gần bạn tại công viên Cầu Giấy.';
    }
    return 'Xin lỗi, tôi chưa có thông tin cho câu hỏi này. Vui lòng thử lại với câu hỏi khác.';
  };

  const appendMessage = (msg: Omit<ChatMessage, 'id'>) => {
    setMessages((prev) => [
      ...prev,
      { ...msg, id: `${Date.now()}-${Math.random()}` },
    ]);
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isSending) return;
    setIsSending(true);
    appendMessage({ text, isUser: true });
    setInput('');

    // giả lập delay trả lời
    setTimeout(() => {
      const answer = generateDummyAnswer(text);
      appendMessage({ text: answer, isUser: false });
      setIsSending(false);
    }, 800);
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
            style={styles.headerBackButton}
            onPress={() => navigation.goBack()}
          >
            <MaterialIcons name="arrow-back" size={24} color="#FFFFFF" />
          </TouchableOpacity>
          <View style={styles.headerTextWrapper}>
            <Text style={styles.headerTitle}>Chat với AI CityLens</Text>
            <Text style={styles.headerSubtitle}>
              Hỏi về ngập, tắc đường, dịch vụ, điểm trú mưa...
            </Text>
          </View>
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
          <TextInput
            style={styles.input}
            value={input}
            onChangeText={setInput}
            placeholder="Hỏi AI về ngập, tắc đường, dịch vụ gần bạn..."
            multiline
            onSubmitEditing={() => handleSend()}
          />
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
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 8,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#20A957',
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#16A34A',
  },
  headerBackButton: {
    marginRight: 8,
    padding: 4,
  },
  headerTextWrapper: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  headerSubtitle: {
    marginTop: 4,
    fontSize: 13,
    color: '#D1FAE5',
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
});

export default AiAssistantScreen;


