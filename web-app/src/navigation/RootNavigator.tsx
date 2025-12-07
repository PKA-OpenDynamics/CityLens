// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MaterialIcons } from '@expo/vector-icons';
import { getFocusedRouteNameFromRoute } from '@react-navigation/native';
import { ActivityIndicator, View } from 'react-native';

// Screens
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import ForgotPasswordScreen from '../screens/ForgotPasswordScreen';
import ExploreScreen from '../screens/ExploreScreen.native';
import MapScreen from '../screens/MapScreen';
import ReportScreen from '../screens/ReportScreen.native';
import ProfileScreen from '../screens/ProfileScreen.native';
import CreateReportScreen from '../screens/CreateReportScreen.native';
import ReportDetailScreen from '../screens/ReportDetailScreen.native';
import AiAssistantScreen from '../screens/AiAssistantScreen.native';
import ChangePasswordScreen from '../screens/ChangePasswordScreen';
import PersonalInfoScreen from '../screens/PersonalInfoScreen';
import WeatherDetailScreen from '../screens/WeatherDetailScreen.native';
import AirQualityDetailScreen from '../screens/AirQualityDetailScreen.native';
import EnvironmentDetailScreen from '../screens/EnvironmentDetailScreen.native';
import { useAuth } from '../contexts/AuthContext';

const Tab = createBottomTabNavigator();
const ReportStack = createNativeStackNavigator();
const RootStack = createNativeStackNavigator();

function ReportStackNavigator() {
  return (
    <ReportStack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <ReportStack.Screen
        name="ReportHome"
        component={ReportScreen}
        options={{
          headerShown: false,
        }}
      />
      <ReportStack.Screen
        name="CreateReport"
        component={CreateReportScreen}
        options={{
          headerShown: false,
        }}
      />
      <ReportStack.Screen
        name="ReportDetail"
        component={ReportDetailScreen}
        options={{
          headerShown: false,
        }}
      />
      <ReportStack.Screen
        name="AiAssistant"
        component={AiAssistantScreen}
        options={{
          headerShown: false,
        }}
      />
    </ReportStack.Navigator>
  );
}

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => {
        const focusedRouteName = getFocusedRouteNameFromRoute(route);

        // Ẩn tab bar khi:
        // - Tab Map được chọn
        // - Đang ở trong Report stack và màn hiện tại là ReportHome hoặc AiAssistant
        let hideTabBar = false;

        if (route.name === 'Map') {
          hideTabBar = true;
        } else if (route.name === 'Report') {
          const reportRouteName = focusedRouteName ?? 'ReportHome';
          hideTabBar =
            reportRouteName === 'ReportHome' ||
            reportRouteName === 'AiAssistant';
        }

        return {
          headerShown: false,
          tabBarActiveTintColor: '#20A957',
          tabBarInactiveTintColor: '#9CA3AF',
          tabBarShowLabel: true,
          tabBarStyle: {
            borderTopWidth: 0.5,
            borderTopColor: '#E5E7EB',
            display: hideTabBar ? 'none' : 'flex',
            height: 60,
            backgroundColor: '#FFFFFF',
            elevation: 8,
            shadowColor: '#000',
            shadowOffset: { width: 0, height: -2 },
            shadowOpacity: 0.1,
            shadowRadius: 4,
          },
          tabBarIcon: ({ color, size, focused }) => {
            let iconName: keyof typeof MaterialIcons.glyphMap = 'public';
            if (route.name === 'Explore') iconName = 'explore';
            if (route.name === 'Map') iconName = 'map';
            if (route.name === 'Report') iconName = 'campaign';
            if (route.name === 'Profile') iconName = 'account-circle';
            return (
              <MaterialIcons 
                name={iconName} 
                size={focused ? 26 : 24} 
                color={color} 
              />
            );
          },
          tabBarLabelStyle: {
            fontSize: 11,
            fontWeight: '500',
          },
        };
      }}
    >
      <Tab.Screen
        name="Explore"
        component={ExploreScreen}
        options={{
          tabBarLabel: 'Khám phá',
        }}
      />
      <Tab.Screen
        name="Map"
        component={MapScreen}
        options={{
          tabBarLabel: 'Bản đồ',
        }}
      />
      <Tab.Screen
        name="Report"
        component={ReportStackNavigator}
        options={{
          tabBarLabel: 'Phản ánh',
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Hồ sơ',
        }}
      />
    </Tab.Navigator>
  );
}

const RootNavigator: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#20A957' }}>
        <ActivityIndicator size="large" color="#FFFFFF" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <RootStack.Navigator screenOptions={{ headerShown: false }}>
        {!isAuthenticated ? (
          // Auth screens
          <>
            <RootStack.Screen name="Login" component={LoginScreen} />
            <RootStack.Screen name="Register" component={RegisterScreen} />
            <RootStack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
          </>
        ) : (
          // Main app screens
          <>
            <RootStack.Screen name="MainTabs" component={TabNavigator} />
            <RootStack.Screen name="Profile" component={ProfileScreen} />
            <RootStack.Screen name="AiAssistant" component={AiAssistantScreen} />
            <RootStack.Screen name="ChangePassword" component={ChangePasswordScreen} />
            <RootStack.Screen name="PersonalInfo" component={PersonalInfoScreen} />
            <RootStack.Screen name="WeatherDetail" component={WeatherDetailScreen} />
            <RootStack.Screen name="AirQualityDetail" component={AirQualityDetailScreen} />
            <RootStack.Screen name="EnvironmentDetail" component={EnvironmentDetailScreen} />
          </>
        )}
      </RootStack.Navigator>
    </NavigationContainer>
  );
};

export default RootNavigator;
