#include <iostream>
#include <vector>

struct StockData {
    double close;
    double short_mavg;
    double long_mavg;
};

int main() {
    std::string symbol = "AAPL";
    int short_window = 50;
    int long_window = 200;

    // Fetch historical data and populate the StockData vector
    std::vector<StockData> data;
    // ...

    // Calculate moving averages
    for (int i = 0; i < data.size(); ++i) {
        double sum_short = 0.0;
        double sum_long = 0.0;

        // Calculate short-term moving average
        int start_short = std::max(0, i - short_window + 1);
        for (int j = start_short; j <= i; ++j) {
            sum_short += data[j].close;
        }
        data[i].short_mavg = sum_short / (i - start_short + 1);

        // Calculate long-term moving average
        int start_long = std::max(0, i - long_window + 1);
        for (int j = start_long; j <= i; ++j) {
            sum_long += data[j].close;
        }
        data[i].long_mavg = sum_long / (i - start_long + 1);
    }

    int position = 0;  // 0: out of market, 1: long position
    double capital = 100000.0;  // Initial capital
    double shares = 0.0;  // Number of shares held
    double commission = 0.005;  // Commission fee per trade

    // Iterate over the data, starting from the long_window index
    for (int i = long_window; i < data.size(); ++i) {
        // Generate buy signal
        if (data[i].short_mavg > data[i].long_mavg && position == 0) {
            double shares_to_buy = capital / data[i].close;
            shares = shares_to_buy;
            capital -= shares_to_buy * data[i].close;
            position = 1;
            std::cout << "Buy " << symbol << " at " << data[i].close << std::endl;
        }

        // Generate sell signal
        else if (data[i].short_mavg < data[i].long_mavg && position == 1) {
            capital += shares * data[i].close * (1.0 - commission);
            shares = 0.0;
            position = 0;
            std::cout << "Sell " << symbol << " at " << data[i].close << std::endl;
        }
    }

    // Calculate final portfolio value
    double portfolio_value = capital + shares * data[data.size() - 1].close;
    std::cout << "Final portfolio value: " << portfolio_value << std::endl;

    return 0;
}
