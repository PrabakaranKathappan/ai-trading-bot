import React, { useState, useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Button, Surface, ActivityIndicator, List, Icon } from 'react-native-paper';
import * as SecureStore from 'expo-secure-store';
import axios from 'axios';
import { MaterialCommunityIcons } from '@expo/vector-icons';

export default function VerificationScreen({ navigation }) {
    const [status, setStatus] = useState({
        server: { status: 'pending', message: 'Checking...' },
        engine: { status: 'pending', message: 'Checking...' },
        auth: { status: 'pending', message: 'Checking...' },
        market_data: { status: 'pending', message: 'Checking...' }
    });
    const [loading, setLoading] = useState(true);
    const [allGood, setAllGood] = useState(false);

    useEffect(() => {
        checkSystem();
    }, []);

    const checkSystem = async () => {
        setLoading(true);
        setAllGood(false);
        try {
            const url = await SecureStore.getItemAsync('bot_url');
            const pin = await SecureStore.getItemAsync('bot_pin');

            if (!url || !pin) {
                setStatus(prev => ({ ...prev, server: { status: 'error', message: 'Missing credentials' } }));
                setLoading(false);
                return;
            }

            const response = await axios.get(`${url}/api/system-check`, {
                headers: { 'X-Access-Pin': pin }
            });

            const data = response.data;
            setStatus(data);

            // Check if everything is OK
            if (data.server.status === 'ok' &&
                data.engine.status === 'ok' &&
                data.auth.status === 'ok' &&
                data.market_data.status === 'ok') {
                setAllGood(true);
            }

        } catch (error) {
            console.log(error);
            setStatus(prev => ({
                ...prev,
                server: { status: 'error', message: 'Connection failed' }
            }));
        } finally {
            setLoading(false);
        }
    };

    const StatusItem = ({ title, item }) => {
        let icon = 'progress-clock';
        let color = 'grey';

        if (item.status === 'ok') {
            icon = 'check-circle';
            color = 'green';
        } else if (item.status === 'error') {
            icon = 'alert-circle';
            color = 'red';
        }

        return (
            <List.Item
                title={title}
                description={item.message}
                left={props => <List.Icon {...props} icon={icon} color={color} />}
            />
        );
    };

    return (
        <View style={styles.container}>
            <Surface style={styles.surface}>
                <Text variant="headlineSmall" style={styles.title}>System Status</Text>

                <StatusItem title="Server Connection" item={status.server} />
                <StatusItem title="Trading Engine" item={status.engine} />
                <StatusItem title="Upstox Auth" item={status.auth} />
                <StatusItem title="Market Data" item={status.market_data} />

                {loading && <ActivityIndicator style={{ marginTop: 20 }} />}

                {!loading && allGood && (
                    <View style={styles.successContainer}>
                        <MaterialCommunityIcons name="check-decagram" size={64} color="green" />
                        <Text variant="headlineMedium" style={{ color: 'green', marginTop: 10 }}>SYSTEM READY</Text>
                        <Text variant="bodyMedium">Your bot is fully operational!</Text>
                    </View>
                )}

                <Button
                    mode="contained"
                    onPress={checkSystem}
                    style={styles.button}
                    loading={loading}
                >
                    Re-Check Status
                </Button>

                <Button
                    mode="outlined"
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
        padding: 20,
        backgroundColor: '#f5f5f5',
        justifyContent: 'center',
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
    button: {
        marginTop: 15,
    },
    successContainer: {
        alignItems: 'center',
        marginVertical: 20,
        padding: 10,
        backgroundColor: '#e8f5e9',
        borderRadius: 10,
    }
});
