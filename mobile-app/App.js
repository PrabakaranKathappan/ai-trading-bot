import 'react-native-gesture-handler';
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Provider as PaperProvider } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';

import LoginScreen from './screens/LoginScreen';
import DashboardScreen from './screens/DashboardScreen';
import SetupScreen from './screens/SetupScreen';
import VerificationScreen from './screens/VerificationScreen';

const Stack = createNativeStackNavigator();

export default function App() {
    return (
        <PaperProvider>
            <NavigationContainer>
                <StatusBar style="auto" />
                <Stack.Navigator
                    initialRouteName="Login"
                    screenOptions={{
                        headerStyle: {
                            backgroundColor: '#f4511e',
                        },
                        headerTintColor: '#fff',
                        headerTitleStyle: {
                            fontWeight: 'bold',
                        },
                    }}
                >
                    <Stack.Screen
                        name="Login"
                        component={LoginScreen}
                        options={{ headerShown: false }}
                    />
                    <Stack.Screen
                        name="Dashboard"
                        component={DashboardScreen}
                        options={{
                            title: 'Trading Bot',
                            headerLeft: null, // Disable back button
                        }}
                    />
                    <Stack.Screen
                        name="Setup"
                        component={SetupScreen}
                        options={{ title: 'Settings' }}
                    />
                    <Stack.Screen
                        name="Verification"
                        component={VerificationScreen}
                        options={{ title: 'System Check' }}
                    />
                </Stack.Navigator>
            </NavigationContainer>
        </PaperProvider>
    );
}
