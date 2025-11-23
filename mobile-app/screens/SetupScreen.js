import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { TextInput, Button, Text, Surface } from 'react-native-paper';
import * as SecureStore from 'expo-secure-store';
import axios from 'axios';

export default function SetupScreen({ navigation }) {
    const [apiKey, setApiKey] = useState('');
    const [apiSecret, setApiSecret] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadSavedKeys();
    }, []);

    const loadSavedKeys = async () => {
        try {
            const savedKey = await SecureStore.getItemAsync('upstox_api_key');
            const savedSecret = await SecureStore.getItemAsync('upstox_api_secret');
            if (savedKey) setApiKey(savedKey);
            if (savedSecret) setApiSecret(savedSecret);
        } catch (error) {
            console.log('Error loading keys', error);
        }
    };

    const handleSave = async () => {
        if (!apiKey || !apiSecret) {
            Alert.alert('Error', 'Please enter both API Key and Secret');
            return;
        }

        setLoading(true);
        try {
            const url = await SecureStore.getItemAsync('bot_url');
            const pin = await SecureStore.getItemAsync('bot_pin');

            // Send to backend
            const response = await axios.post(`${url}/api/configure`,
                { api_key: apiKey, api_secret: apiSecret },
                { headers: { 'X-Access-Pin': pin } }
            );

            if (response.status === 200) {
                // Save locally
                await SecureStore.setItemAsync('upstox_api_key', apiKey);
                await SecureStore.setItemAsync('upstox_api_secret', apiSecret);

                Alert.alert('Success', 'Credentials updated successfully', [
                    { text: 'OK', onPress: () => navigation.goBack() }
                ]);
            }
        } catch (error) {
            console.log(error);
            Alert.alert('Error', 'Failed to update credentials. Check connection.');
        } finally {
            setLoading(false);
        }
    };

    const handleAuthenticate = async () => {
        setLoading(true);
        try {
            const url = await SecureStore.getItemAsync('bot_url');
            const pin = await SecureStore.getItemAsync('bot_pin');

            const response = await axios.get(`${url}/login`, {
                headers: { 'X-Access-Pin': pin }
            });

            if (response.data.auth_url) {
                // Open in browser
                import('react-native').then(({ Linking }) => {
                    Linking.openURL(response.data.auth_url);
                });
            } else {
                Alert.alert('Error', 'Could not get auth URL');
            }
        } catch (error) {
            console.log(error);
            Alert.alert('Error', 'Failed to start authentication');
        } finally {
            setLoading(false);
        }
    };

    return (
        <View style={styles.container}>
            <Surface style={styles.surface}>
                <Text variant="headlineSmall" style={styles.title}>API Configuration</Text>
                <Text variant="bodyMedium" style={styles.subtitle}>
                    Enter your Upstox API credentials to start trading.
                </Text>

                <TextInput
                    label="Upstox API Key"
                    value={apiKey}
                    onChangeText={setApiKey}
                    mode="outlined"
                    style={styles.input}
                    autoCapitalize="none"
                />

                <TextInput
                    label="Upstox API Secret"
                    value={apiSecret}
                    onChangeText={setApiSecret}
                    mode="outlined"
                    secureTextEntry
                    style={styles.input}
                />

                <Button
                    mode="contained"
                    onPress={handleSave}
                    loading={loading}
                    style={styles.button}
                >
                    Save Credentials
                </Button>

                <Button
                    mode="contained-tonal"
                    icon="login"
                    onPress={handleAuthenticate}
                    style={[styles.button, { marginTop: 20, backgroundColor: '#e3f2fd' }]}
                >
                    Authenticate with Upstox
                </Button>

                <Button
                    mode="contained-tonal"
                    icon="check-network-outline"
                    onPress={() => navigation.navigate('Verification')}
                    style={[styles.button, { backgroundColor: '#e8f5e9' }]}
                >
                    Check System Status
                </Button>

                <Button
                    mode="text"
                    onPress={() => navigation.goBack()}
                    style={styles.button}
                >
                    Back
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
        marginBottom: 10,
        fontWeight: 'bold',
    },
    subtitle: {
        textAlign: 'center',
        marginBottom: 20,
        color: '#666',
    },
    input: {
        marginBottom: 15,
    },
    button: {
        marginTop: 10,
    },
});
