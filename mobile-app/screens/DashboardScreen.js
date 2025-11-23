import React, { useState, useEffect, useCallback } from 'react';
import { View, ScrollView, StyleSheet, RefreshControl, Alert } from 'react-native';
import { Text, Card, Button, Chip, Divider, IconButton, FAB } from 'react-native-paper';
import * as SecureStore from 'expo-secure-store';
import axios from 'axios';
import { useFocusEffect } from '@react-navigation/native';

export default function DashboardScreen({ navigation }) {
    const [data, setData] = useState(null);
    const [refreshing, setRefreshing] = useState(false);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const url = await SecureStore.getItemAsync('bot_url');
            const pin = await SecureStore.getItemAsync('bot_pin');

            if (!url || !pin) {
                navigation.replace('Login');
                return;
            }

            const response = await axios.get(`${url}/api/status`, {
                headers: { 'X-Access-Pin': pin }
            });

            setData(response.data);
        } catch (error) {
            console.log(error);
            if (error.response && error.response.status === 401) {
                navigation.replace('Login');
            }
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useFocusEffect(
        useCallback(() => {
            fetchData();
            const interval = setInterval(fetchData, 5000); // Auto refresh
            return () => clearInterval(interval);
        }, [])
    );

    const onRefresh = () => {
        setRefreshing(true);
        fetchData();
    };

    const handleClosePosition = async (symbol) => {
        try {
            const url = await SecureStore.getItemAsync('bot_url');
            const pin = await SecureStore.getItemAsync('bot_pin');

            await axios.post(`${url}/api/positions/close`,
                { symbol },
                { headers: { 'X-Access-Pin': pin } }
            );

            Alert.alert('Success', 'Close order sent');
            fetchData();
        } catch (error) {
            Alert.alert('Error', 'Failed to close position');
        }
    };

    const handleSquareOff = async () => {
        Alert.alert(
            'Confirm Square Off',
            'Are you sure you want to close ALL positions?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Yes, Close All',
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            const url = await SecureStore.getItemAsync('bot_url');
                            const pin = await SecureStore.getItemAsync('bot_pin');

                            await axios.post(`${url}/api/control/square-off`, {},
                                { headers: { 'X-Access-Pin': pin } }
                            );
                            Alert.alert('Success', 'Square off initiated');
                            fetchData();
                        } catch (error) {
                            Alert.alert('Error', 'Failed to square off');
                        }
                    }
                }
            ]
        );
    };

    if (loading && !data) {
        return (
            <View style={styles.center}>
                <Text>Loading...</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <ScrollView
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
                }
            >
                {/* Status Card */}
                <Card style={styles.card}>
                    <Card.Content>
                        <View style={styles.row}>
                            <Text variant="titleLarge">Status</Text>
                            <Chip icon="circle" mode="outlined" selectedColor={data?.status === 'running' ? 'green' : 'red'}>
                                {data?.status?.toUpperCase()}
                            </Chip>
                        </View>
                        <Text variant="bodyMedium" style={{ marginTop: 5 }}>Mode: {data?.mode?.toUpperCase()}</Text>
                        <Text variant="bodyMedium">Capital: ₹{data?.capital?.toLocaleString()}</Text>
                    </Card.Content>
                </Card>

                {/* P&L Card */}
                <Card style={styles.card}>
                    <Card.Content>
                        <Text variant="titleMedium">Today's P&L</Text>
                        <Text variant="displayMedium" style={{
                            color: (data?.today_pnl?.total_pnl || 0) >= 0 ? 'green' : 'red',
                            fontWeight: 'bold'
                        }}>
                            ₹{data?.today_pnl?.total_pnl?.toFixed(2) || '0.00'}
                        </Text>
                        <Text variant="bodySmall">
                            {(data?.today_pnl?.pnl_percent || 0).toFixed(2)}%
                        </Text>
                    </Card.Content>
                </Card>

                {/* Positions */}
                <Text variant="titleLarge" style={styles.sectionTitle}>Open Positions</Text>
                {data?.positions?.length === 0 ? (
                    <Text style={styles.emptyText}>No open positions</Text>
                ) : (
                    data?.positions?.map((pos, index) => (
                        <Card key={index} style={styles.positionCard}>
                            <Card.Content>
                                <View style={styles.row}>
                                    <Text variant="titleMedium">{pos.symbol}</Text>
                                    <Text variant="titleMedium" style={{ color: pos.unrealized_pnl >= 0 ? 'green' : 'red' }}>
                                        ₹{pos.unrealized_pnl?.toFixed(2)}
                                    </Text>
                                </View>
                                <View style={styles.row}>
                                    <Text>{pos.quantity} Qty @ {pos.entry_price}</Text>
                                    <Text>LTP: {pos.current_price}</Text>
                                </View>
                            </Card.Content>
                            <Card.Actions>
                                <Button
                                    mode="contained-tonal"
                                    textColor="red"
                                    onPress={() => handleClosePosition(pos.symbol)}
                                >
                                    Close Position
                                </Button>
                            </Card.Actions>
                        </Card>
                    ))
                )}

                <View style={{ height: 80 }} />
            </ScrollView>

            <FAB
                icon="cog"
                style={styles.fab}
                onPress={() => navigation.navigate('Setup')}
                label="Settings"
            />

            {data?.positions?.length > 0 && (
                <FAB
                    icon="close-circle"
                    style={[styles.fab, { bottom: 90, backgroundColor: '#ffebee' }]}
                    color="red"
                    onPress={handleSquareOff}
                    label="Square Off All"
                />
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
        padding: 10,
    },
    center: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    card: {
        marginBottom: 10,
        backgroundColor: 'white',
    },
    positionCard: {
        marginBottom: 10,
        backgroundColor: 'white',
        borderLeftWidth: 4,
        borderLeftColor: '#2196F3',
    },
    row: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 5,
    },
    sectionTitle: {
        marginVertical: 10,
        fontWeight: 'bold',
    },
    emptyText: {
        textAlign: 'center',
        color: '#666',
        marginTop: 20,
    },
    fab: {
        position: 'absolute',
        margin: 16,
        right: 0,
        bottom: 0,
    },
});
