// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in development
    if (__DEV__) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      // Ignore errors from browser extensions (Solana, MetaMask, etc.)
      const errorMessage = this.state.error?.message || '';
      const errorStack = this.state.error?.stack || '';
      const errorName = this.state.error?.name || '';
      const fullErrorText = `${errorName} ${errorMessage} ${errorStack}`.toLowerCase();
      
      const isExtensionError = 
        fullErrorText.includes('solana') ||
        fullErrorText.includes('metamask') ||
        fullErrorText.includes('wallet') ||
        fullErrorText.includes('chrome-extension') ||
        fullErrorText.includes('moz-extension') ||
        fullErrorText.includes('solanaactionscontentscript') ||
        fullErrorText.includes('wx') ||
        fullErrorText.includes('b4');

      if (isExtensionError) {
        // Silently ignore extension errors and render children
        // Reset error state to prevent infinite loop
        this.setState({
          hasError: false,
          error: null,
          errorInfo: null,
        });
        return this.props.children;
      }

      return (
        <View style={styles.container}>
          <ScrollView contentContainerStyle={styles.scrollContent}>
            <Text style={styles.title}>Đã xảy ra lỗi</Text>
            <Text style={styles.message}>
              {this.state.error?.message || 'Lỗi không xác định'}
            </Text>
            {__DEV__ && this.state.errorInfo && (
              <View style={styles.errorInfo}>
                <Text style={styles.errorInfoTitle}>Chi tiết lỗi:</Text>
                <Text style={styles.errorInfoText}>
                  {this.state.errorInfo.componentStack}
                </Text>
              </View>
            )}
            <TouchableOpacity style={styles.button} onPress={this.handleReset}>
              <Text style={styles.buttonText}>Thử lại</Text>
            </TouchableOpacity>
          </ScrollView>
        </View>
      );
    }

    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
    textAlign: 'center',
  },
  message: {
    fontSize: 16,
    color: '#666',
    marginBottom: 24,
    textAlign: 'center',
  },
  errorInfo: {
    width: '100%',
    backgroundColor: '#f5f5f5',
    padding: 12,
    borderRadius: 8,
    marginBottom: 24,
  },
  errorInfoTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  errorInfoText: {
    fontSize: 12,
    color: '#666',
    fontFamily: 'monospace',
  },
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ErrorBoundary;

