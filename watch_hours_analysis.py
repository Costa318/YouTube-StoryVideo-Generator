#!/usr/bin/env python3
"""
Calculate total watch hours and analyze channel performance efficiency.
"""

import json
from pathlib import Path

def calculate_watch_hours():
    """Calculate total watch hours for each channel."""
    
    # Load analysis data
    with open('research/analysis_summary.json', 'r') as f:
        data = json.load(f)
    
    print("📊 HORROR CHANNEL WATCH HOURS ANALYSIS")
    print("=" * 60)
    
    channel_stats = []
    
    # Get Mr. Nightmare data separately (from our earlier analysis)
    mr_nightmare_data = {
        'name': 'Mr. Nightmare',
        'videos': [
            {'title': '3 Scary TRUE Horror Stories', 'views': 851527, 'duration': 1387},
            {'title': '3 Disturbing TRUE "Being Watched" Horror Stories', 'views': 702718, 'duration': 1046},
            {'title': '3 Very Creepy TRUE Night Drive Horror Stories', 'views': 667414, 'duration': 1234},
            {'title': '4 Disturbing TRUE Trespassing Horror Stories', 'views': 663170, 'duration': 1661},
            {'title': '3 Scary TRUE Summer Vacation Horror Stories', 'views': 494441, 'duration': 1621},
            {'title': '7 Most Disturbing Things Found in the Woods', 'views': 446258, 'duration': 1099},
            {'title': '3 Disturbing TRUE Hidden Camera Horror Stories', 'views': 240022, 'duration': 1251}
        ]
    }
    
    # Calculate Mr. Nightmare stats
    total_views = sum(v['views'] for v in mr_nightmare_data['videos'])
    total_watch_hours = sum(v['views'] * v['duration'] / 3600 for v in mr_nightmare_data['videos'])
    avg_duration = sum(v['duration'] for v in mr_nightmare_data['videos']) / len(mr_nightmare_data['videos'])
    
    channel_stats.append({
        'name': 'Mr. Nightmare',
        'videos': len(mr_nightmare_data['videos']),
        'total_views': total_views,
        'total_watch_hours': total_watch_hours,
        'avg_duration_mins': avg_duration / 60,
        'avg_views_per_video': total_views / len(mr_nightmare_data['videos']),
        'watch_hours_per_video': total_watch_hours / len(mr_nightmare_data['videos'])
    })
    
    # Calculate stats for other channels
    for channel_name, channel_data in data['channels'].items():
        if channel_data['videos_found'] == 0:
            continue
            
        total_views = 0
        total_duration = 0
        total_watch_hours = 0
        
        for video in channel_data['videos']:
            views = video['view_count']
            duration = float(video['duration'])
            
            total_views += views
            total_duration += duration
            total_watch_hours += (views * duration) / 3600  # Convert to hours
        
        avg_duration = total_duration / len(channel_data['videos'])
        
        channel_stats.append({
            'name': channel_name,
            'videos': channel_data['videos_found'],
            'total_views': total_views,
            'total_watch_hours': total_watch_hours,
            'avg_duration_mins': avg_duration / 60,
            'avg_views_per_video': total_views / channel_data['videos_found'],
            'watch_hours_per_video': total_watch_hours / channel_data['videos_found']
        })
    
    # Sort by total watch hours (descending)
    channel_stats.sort(key=lambda x: x['total_watch_hours'], reverse=True)
    
    # Display results
    print(f"{'Channel':<25} {'Videos':<7} {'Total Views':<12} {'Watch Hours':<12} {'Avg Duration':<12} {'Efficiency':<10}")
    print("-" * 90)
    
    for i, stats in enumerate(channel_stats, 1):
        efficiency = stats['watch_hours_per_video'] / 1000  # Thousands of watch hours per video
        print(f"{i}. {stats['name']:<22} {stats['videos']:<7} "
              f"{stats['total_views']:,<11} {stats['total_watch_hours']:,.0f}<11 "
              f"{stats['avg_duration_mins']:.1f} mins<8 {efficiency:.1f}K<10")
    
    print("\n📈 KEY INSIGHTS:")
    print("=" * 40)
    
    # Find the winner
    winner = channel_stats[0]
    print(f"🏆 WATCH HOURS CHAMPION: {winner['name']}")
    print(f"   • Total Watch Hours: {winner['total_watch_hours']:,.0f} hours")
    print(f"   • Efficiency: {winner['watch_hours_per_video']/1000:.1f}K watch hours per video")
    
    print(f"\n🎯 MOST EFFICIENT (Watch Hours per Video):")
    efficiency_sorted = sorted(channel_stats, key=lambda x: x['watch_hours_per_video'], reverse=True)
    most_efficient = efficiency_sorted[0]
    print(f"   • {most_efficient['name']}: {most_efficient['watch_hours_per_video']/1000:.1f}K watch hours per video")
    
    print(f"\n⏱️ LONGEST CONTENT:")
    duration_sorted = sorted(channel_stats, key=lambda x: x['avg_duration_mins'], reverse=True)
    longest = duration_sorted[0]
    print(f"   • {longest['name']}: {longest['avg_duration_mins']:.1f} minutes average")
    
    print(f"\n👁️ HIGHEST VIEW COUNT:")
    views_sorted = sorted(channel_stats, key=lambda x: x['avg_views_per_video'], reverse=True)
    highest_views = views_sorted[0]
    print(f"   • {highest_views['name']}: {highest_views['avg_views_per_video']:,.0f} average views per video")
    
    # Calculate total dataset
    total_watch_hours_all = sum(s['total_watch_hours'] for s in channel_stats)
    total_videos_all = sum(s['videos'] for s in channel_stats)
    
    print(f"\n📊 COMPLETE DATASET:")
    print(f"   • Total Videos Analyzed: {total_videos_all}")
    print(f"   • Combined Watch Hours: {total_watch_hours_all:,.0f} hours")
    print(f"   • Equivalent Days: {total_watch_hours_all/24:.1f} days of content")
    
    return channel_stats

if __name__ == '__main__':
    calculate_watch_hours()