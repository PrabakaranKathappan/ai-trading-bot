import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { TextInput, Button, Text, Surface } from 'react-native-paper';
import * as SecureStore from 'expo-secure-store';
import axios from 'axios';

export default function LoginScreen({ navigation }) {
    const [url, setUrl] = useState('https://ai-trading-bot-npoh.onrender.com');
    const [pin, setPin] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadSavedCredentials();
    }, []);

    const loadSavedCredentials = async () => {
        try {
            const savedUrl = await SecureStore.getItemAsync('bot_url');
            const savedPin = await SecureStore.getItemAsync('bot_pin');
            if (savedUrl) setUrl(savedUrl);
            if (savedPin) setPin(savedPin);
        } catch (error) {
            console.log('Error loading credentials', error);
        }
    };

    const handleLogin = async () => {
        if (!url || !pin) {
            Alert.alert('Error', 'Please enter both URL and PIN');
            return;
        }

        setLoading(true);
        try {
            // Clean URL and PIN
            const cleanUrl = url.trim().replace(/\/$/, '');
            const cleanPin = pin.trim();

            // Test connection
            const response = await axios.get(`${cleanUrl}/health`, {
                headers: { 'X-Access-Pin': cleanPin }
            });

            if (response.status === 200) {
                // Save credentials
                await SecureStore.setItemAsync('bot_url', cleanUrl);
                await SecureStore.setItemAsync('bot_pin', cleanPin);

                // Navigate to Dashboard
                navigation.replace('Dashboard');
            }
        } catch (error) {
            console.log(error);
            if (error.response) {
                if (error.response.status === 401) {
                    Alert.alert('Error', 'Invalid PIN');
                } else {
                    Alert.alert('Server Error', `Status: ${error.response.status}\n${JSON.stringify(error.response.data)}`);
                }
            } else if (error.request) {
                Alert.alert('Network Error', 'No response received. Check internet or CORS.');
                console.log('Request error:', error.request);
            } else {
                Alert.alert('Error', error.message);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <View style={styles.container}>
            <Surface style={styles.surface}>
                <Text variant="headlineMedium" style={styles.title}>AI Trading Bot</Text>

                <TextInput
                    label="Bot URL"
                    value={url}
                    onChangeText={setUrl}
                    mode="outlined"
                    style={styles.input}
                    autoCapitalize="none"
                />

                <TextInput
                    label="Access PIN / Password"
                    value={pin}
                    onChangeText={setPin}
                    mode="outlined"
                    secureTextEntry
                    style={styles.input}
                />

                <Button
                    mode="contained"
                    onPress={handleLogin}
                    loading={loading}
                    style={styles.button}
                >
                    Connect
                </Button>
            </Surface>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        padding: 20,
        backgroundColor: '#f5f5f5',
    },
    surface: {
        padding: 20,
        borderRadius: 10,
        elevation: 4,
    },
    title: {
        textAlign: 'center',
        marginBottom: 20,
        fontWeight: 'bold',
    },
    input: {
        marginBottom: 15,
    },
    button: {
        marginTop: 10,
    },
});
