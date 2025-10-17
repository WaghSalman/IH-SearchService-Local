from flask import Blueprint, request, jsonify, make_response
import logging
from model.influencer import Influencer

from enums.platform import Platform
from model.metrics import Metrics, MetricsEngagementRateIndex, MetricsFollowersIndex
from utils.format_utils import format_number_short
from utils.pagination import paginate_list, encode_token, decode_token

bp = Blueprint('influencer_metrics', __name__)


def _paginate_response(result_iterable):
    """Helper to paginate an iterable result using request args limit/next_token.
    Returns tuple (items_list, next_token_or_none).
    """
    # Note: result_iterable may be either:
    #  - an iterable of items
    #  - a tuple (iterable, last_evaluated_key) from a DB-backed call
    limit = request.args.get('limit', type=int)
    next_token = request.args.get('next_token', type=str)

    # If model returned a (iterable, last_key) tuple, prefer server-side cursor
    if isinstance(result_iterable, tuple) and len(result_iterable) == 2:
        iterable, last_key = result_iterable
        items = [r for r in iterable]
        token = encode_token({'type': 'last_key', 'key': last_key}) if last_key else None
        return items, token

    # Otherwise fall back to in-memory pagination for plain iterables
    items = list(result_iterable)
    if limit is None and next_token is None:
        return items, None
    page_items, out_token = paginate_list(items, limit or 50, next_token)
    return page_items, out_token


@bp.route('/searchById', methods=['GET'])
def search_by_id():
    influencer_id = request.args.get('influencer_id')
    if not influencer_id:
        return make_response(jsonify({'success': False, 'error': 'No influencer_id parameter provided'}), 400)
    try:
        result = Influencer.search_by_id(influencer_id)
        items, out_token = _paginate_response(result)
        influencers = [influencer.to_dict() for influencer in items]
        body = {'success': True, 'data': influencers}
        if out_token:
            body['next_token'] = out_token
        return make_response(jsonify(body), 200)
    except Exception as e:
        logging.error(f"Error searching by ID: {str(e)}")
        return make_response(jsonify({'error': 'Failed to search by ID'}), 500)


@bp.route('/searchByName', methods=['GET'])
def search_by_name():
    name = request.args.get('name')
    if not name:
        return make_response(jsonify({'success': False, 'error': 'No name parameter provided'}), 400)
    try:
        # Support pagination via ?limit=<n>&next_token=<token>
        limit = request.args.get('limit', type=int)
        next_token = request.args.get('next_token', type=str)
        exclusive_start_key = None
        if next_token:
            try:
                decoded = decode_token(next_token)
                if isinstance(decoded, dict) and decoded.get('type') == 'last_key':
                    exclusive_start_key = decoded.get('key')
            except Exception:
                return make_response(jsonify({'success': False, 'error': 'Invalid next_token'}), 400)

        result = Influencer.search_by_name(name, limit=limit, exclusive_start_key=exclusive_start_key)
        items, out_token = _paginate_response(result)
        influencers = [influencer.to_dict() for influencer in items]
        body = {'success': True, 'data': influencers}
        if out_token:
            body['next_token'] = out_token
        return make_response(jsonify(body), 200)
    except Exception as e:
        logging.error(f"Error searching by name: {str(e)}")
        return make_response(jsonify({'success': False, 'error': 'Failed to search by name'}), 500)


@bp.route('/searchByLocation', methods=['GET'])
def search_by_location():
    location = request.args.get('location')
    if not location:
        return make_response(jsonify({'success': False, 'error': 'No location parameter provided'}), 400)
    try:
        limit = request.args.get('limit', type=int)
        next_token = request.args.get('next_token', type=str)
        exclusive_start_key = None
        if next_token:
            try:
                decoded = decode_token(next_token)
                if isinstance(decoded, dict) and decoded.get('type') == 'last_key':
                    exclusive_start_key = decoded.get('key')
            except Exception:
                return make_response(jsonify({'success': False, 'error': 'Invalid next_token'}), 400)
        result = Influencer.search_by_location(location, limit=limit, exclusive_start_key=exclusive_start_key)
        items, out_token = _paginate_response(result)
        influencers = [influencer.to_dict() for influencer in items]
        body = {'success': True, 'data': influencers}
        if out_token:
            body['next_token'] = out_token
        return make_response(jsonify(body), 200)
    except Exception as e:
        logging.error(f"Error searching by location: {str(e)}")
        return make_response(jsonify({'success': False, 'error': 'Failed to search by location'}), 500)


@bp.route('/searchByFilters', methods=['GET'])
def search_by_filters():
    influencer_id = request.args.get('influencer_id')
    name = request.args.get('name')
    location = request.args.get('location')
    try:
        limit = request.args.get('limit', type=int)
        next_token = request.args.get('next_token', type=str)
        exclusive_start_key = None
        if next_token:
            try:
                decoded = decode_token(next_token)
                if isinstance(decoded, dict) and decoded.get('type') == 'last_key':
                    exclusive_start_key = decoded.get('key')
            except Exception:
                return make_response(jsonify({'success': False, 'error': 'Invalid next_token'}), 400)

        result = Influencer.search_by_filters(influencer_id, name, location)
        items, out_token = _paginate_response(result)
        influencers = [influencer.to_dict() for influencer in items]
        body = {'success': True, 'data': influencers}
        if out_token:
            body['next_token'] = out_token
        return jsonify(body), 200
    except Exception as e:
        logging.error(f"Error searching by filters: {str(e)}")
        return make_response(jsonify({'success': False, 'error': 'Failed to search by filters'}), 500)


@bp.route('/searchByPlatform', methods=['GET'])
def search_by_platform():
    platform = request.args.get('platform')
    if not platform:
        return make_response(jsonify({'success': False, 'error': 'No platform parameter provided'}), 400)
    try:
        platform_enum = Platform[platform.upper()]
        limit = request.args.get('limit', type=int)
        next_token = request.args.get('next_token', type=str)
        exclusive_start_key = None
        if next_token:
            try:
                decoded = decode_token(next_token)
                if isinstance(decoded, dict) and decoded.get('type') == 'last_key':
                    exclusive_start_key = decoded.get('key')
            except Exception:
                return make_response(jsonify({'success': False, 'error': 'Invalid next_token'}), 400)
        result = Influencer.search_by_platform(platform_enum, limit=limit, exclusive_start_key=exclusive_start_key)
        if result is None:
            result = []
        items, out_token = _paginate_response(result)
        influencers = [influencer.to_dict() for influencer in items]
        body = {'success': True, 'data': influencers}
        if out_token:
            body['next_token'] = out_token
        return make_response(jsonify(body), 200)
    except KeyError:
        return make_response(jsonify({'success': False, 'error': f"Invalid platform: {platform}"}), 400)
    except Exception as e:
        logging.error(f"Error searching by platform: {str(e)}")
        return make_response(jsonify({'success': False, 'error': 'Failed to search by platform'}), 500)


@bp.route('/searchByCategory', methods=['GET'])
def search_by_category():
    category = request.args.get('category')
    if not category:
        return make_response(jsonify({'success': False, 'error': 'No category parameter provided'}), 400)
    try:
        # Support comma-separated list of categories
        categories = [c.strip().upper() for c in category.split(',') if c.strip()]
        from enums.category import Category
        # Validate category strings by trying to map them to the enum; support mocked enums
        valid_values = []
        for c in categories:
            try:
                enum_val = Category[c]
                # enum_val may be an Enum with .value or a raw string in tests
                valid_values.append(getattr(enum_val, 'value', enum_val))
            except KeyError:
                return make_response(jsonify({'success': False, 'error': f"Invalid category: {c}"}), 400)

        # Call the Influencer method with normalized string values
        limit = request.args.get('limit', type=int)
        next_token = request.args.get('next_token', type=str)
        exclusive_start_key = None
        if next_token:
            try:
                decoded = decode_token(next_token)
                if isinstance(decoded, dict) and decoded.get('type') == 'last_key':
                    exclusive_start_key = decoded.get('key')
            except Exception:
                return make_response(jsonify({'success': False, 'error': 'Invalid next_token'}), 400)

        result = Influencer.search_by_category(valid_values, limit=limit, exclusive_start_key=exclusive_start_key)
        if result is None:
            result = []
        items, out_token = _paginate_response(result)
        influencers = [influencer.to_dict() for influencer in items]
        body = {'success': True, 'data': influencers}
        if out_token:
            body['next_token'] = out_token
        return make_response(jsonify(body), 200)
    except KeyError:
        return make_response(jsonify({'success': False, 'error': f"Invalid category: {category}"}), 400)
    except Exception as e:
        logging.error(f"Error searching by category: {str(e)}")
        return make_response(jsonify({'success': False, 'error': 'Failed to search by category'}), 500)


@bp.route('/searchByGender', methods=['GET'])
def search_by_gender():
    gender = request.args.get('gender')
    if not gender:
        return make_response(jsonify({'success': False, 'error': 'No gender parameter provided'}), 400)
    try:
        from enums.gender import Gender
        gender_enum = Gender[gender.upper()]
        limit = request.args.get('limit', type=int)
        next_token = request.args.get('next_token', type=str)
        exclusive_start_key = None
        if next_token:
            try:
                decoded = decode_token(next_token)
                if isinstance(decoded, dict) and decoded.get('type') == 'last_key':
                    exclusive_start_key = decoded.get('key')
            except Exception:
                return make_response(jsonify({'success': False, 'error': 'Invalid next_token'}), 400)
        result = Influencer.search_by_gender(gender_enum, limit=limit, exclusive_start_key=exclusive_start_key)
        if result is None:
            result = []
        items, out_token = _paginate_response(result)
        influencers = [influencer.to_dict() for influencer in items]
        body = {'success': True, 'data': influencers}
        if out_token:
            body['next_token'] = out_token
        return make_response(jsonify(body), 200)
    except KeyError:
        return make_response(jsonify({'success': False, 'error': f"Invalid gender: {gender}"}), 400)
    except Exception as e:
        logging.error(f"Error searching by gender: {str(e)}")
        return make_response(jsonify({'success': False, 'error': 'Failed to search by gender'}), 500)


@bp.route('/search_by_metrics', methods=['POST'])
def search_by_metrics():
    try:
        data = request.json
        metrics_ranges = data.get('metrics_ranges', {})
        platform = data.get('platform', None)
        limit = request.args.get('limit', type=int)
        next_token = request.args.get('next_token', type=str)
        exclusive_start_key = None
        if next_token:
            try:
                decoded = decode_token(next_token)
                if isinstance(decoded, dict) and decoded.get('type') == 'last_key':
                    exclusive_start_key = decoded.get('key')
            except Exception:
                return make_response(jsonify({'success': False, 'error': 'Invalid next_token'}), 400)

        results = Influencer.search_by_metrics(metrics_ranges, platform)
        items, out_token = _paginate_response(results)
        results_dict = [influencer.to_dict() for influencer in items]
        body = {"success": True, "data": results_dict}
        if out_token:
            body['next_token'] = out_token
        return jsonify(body), 200
    except Exception as e:
        logging.error(f"Error searching by metrics: {str(e)}")
        return make_response(jsonify({'success': False, 'error': 'Failed to search by metrics'}), 500)


@bp.route('/searchByEngagementRate', methods=['GET'])
def search_by_engagement_rate():
    min_engagement_rate = request.args.get('min_engagement_rate', type=float)
    max_engagement_rate = request.args.get('max_engagement_rate', type=float)
    platform = request.args.get('platform', type=str)
    if not platform:
        return make_response(jsonify({'success': False, 'error': 'No platform parameter provided'}), 400)
    from enums.platform import Platform
    platform_enum = Platform[platform.upper()]
    if min_engagement_rate is None:
        return make_response(jsonify({'success': False, 'error': 'No min_engagement_rate parameter provided'}), 400)
    try:
        result = Metrics.search_by_engagement_rate(min_engagement_rate, max_engagement_rate, platform_enum)
        items, out_token = _paginate_response(result)
        metrics = [m.to_dict() for m in items]
        body = {'success': True, 'data': metrics}
        if out_token:
            body['next_token'] = out_token
        return make_response(jsonify(body), 200)
    except Exception as e:
        logging.error(f"Error searching by engagement rate: {str(e)}")
        return make_response(jsonify({'success': False, 'error': 'Failed to search by engagement rate'}), 500)


@bp.route('/searchByFollowersCount', methods=['GET'])
def search_by_followers_count():
    min_followers = request.args.get('min_followers', type=int)
    max_followers = request.args.get('max_followers', type=int)
    platform = request.args.get('platform', type=str)
    if not platform:
        return make_response(jsonify({'success': False, 'error': 'No platform parameter provided'}), 400)
    from enums.platform import Platform
    platform_enum = Platform[platform.upper()]
    if min_followers is None:
        return make_response(jsonify({'success': False, 'error': 'No min_followers parameter provided'}), 400)
    try:
        result = Metrics.search_by_followers_count(min_followers, max_followers, platform_enum)
        items, out_token = _paginate_response(result)
        metrics = [m.to_dict() for m in items]
        body = {'success': True, 'data': metrics}
        if out_token:
            body['next_token'] = out_token
        return make_response(jsonify(body), 200)
    except Exception as e:
        logging.error(f"Error searching by followers count: {str(e)}")
        return make_response(jsonify({'success': False, 'error': 'Failed to search by followers count'}), 500)


@bp.route('/searchInfluencers', methods=['GET'])
def search_influencers():
    try:
        name_q = request.args.get("name", type=str)
        location_q = request.args.get("location", type=str)
        gender_q = request.args.get("gender", type=str)
        platform_q = request.args.get("platform", type=str)
        min_foll = request.args.get("min_followers", type=int)
        max_foll = request.args.get("max_followers", type=int)
        min_eng_rate = request.args.get("min_engagement_rate", type=float)
        max_eng_rate = request.args.get("max_engagement_rate", type=float)

        influencer_ids = None

        # If a platform is provided but invalid, return empty results early
        if platform_q:
            try:
                from enums.platform import Platform as _P
                _P[platform_q.upper()]
            except Exception:
                return make_response(jsonify({"success": True, "data": []}), 200)

        if platform_q and ((min_foll is not None or max_foll is not None)
                           or (min_eng_rate is not None or max_eng_rate is not None)):
            from enums.platform import Platform
            try:
                platform_enum = Platform[platform_q.upper()]
            except KeyError:
                # Treat invalid platform as no matches (return empty list with 200)
                return make_response(jsonify({"success": True, "data": []}), 200)

            ids_sets = []

            if min_foll is not None or max_foll is not None:
                if min_foll is None:
                    min_foll = 0
                if max_foll is None:
                    max_foll = 10**12
                try:
                    metric_hits = Metrics.platform_followers_idx.query(
                        platform_enum,
                        MetricsFollowersIndex.total_followers.between(
                            min_foll, max_foll)
                    )
                    ids_sets.append({m.influencer_id for m in metric_hits})
                except Exception as e:
                    logging.error(f"Error querying metrics for followers: {e}")
                    return make_response(jsonify({'success': False,
                                                  'error': 'Failed to query metrics for followers'}), 500)

            if min_eng_rate is not None or max_eng_rate is not None:
                if min_eng_rate is None:
                    min_eng_rate = 0.0
                if max_eng_rate is None:
                    max_eng_rate = 100.0
                try:
                    metric_hits = Metrics.platform_engagement_rate_idx.query(
                        platform_enum,
                        MetricsEngagementRateIndex.engagement_rate.between(
                            min_eng_rate, max_eng_rate)
                    )
                    ids_sets.append({m.influencer_id for m in metric_hits})
                except Exception as e:
                    logging.error(
                        f"Error querying metrics for engagement rate: {e}")
                    return make_response(jsonify({'success': False,
                                                  'error': 'Failed to query metrics for engagement rate'}), 500)

            if ids_sets:
                influencer_ids = set.intersection(
                    *ids_sets) if len(ids_sets) > 1 else ids_sets[0]
            else:
                influencer_ids = None

            if influencer_ids is not None and not influencer_ids:
                return make_response(jsonify({"success": True, "data": []}), 200)

        influencers = []
        try:
            if influencer_ids is not None:
                for inf in Influencer.batch_get(list(influencer_ids)):
                    influencers.append(inf)
            else:
                influencers = list(Influencer.scan())
        except Exception as e:
            logging.error(f"Error loading influencers: {e}")
            return make_response(jsonify({'success': False,
                                          'error': 'Failed to load influencers'}), 500)

        def matches(inf):
            if name_q and name_q.lower() not in (inf.name or "").lower():
                return False
            if location_q and (inf.location or "") != location_q:
                return False
            if gender_q:
                gender_val = getattr(inf.gender, "value", None)
                if not gender_val or gender_val.lower() != gender_q.lower():
                    return False
            if platform_q:
                if not any(
                    getattr(p, "platform", None) and getattr(
                        p.platform, "value", "").lower() == platform_q.lower()
                    for p in getattr(inf, "platforms", [])
                ):
                    return False
            return True

        filtered = [inf for inf in influencers if matches(inf)]

        # Apply pagination to filtered influencers
        items, out_token = _paginate_response(filtered)
        filtered = items

        influencer_ids_list = [inf.influencer_id for inf in filtered]
        metrics_map = {}
        if influencer_ids_list:
            try:
                metrics1 = []
                for influencer_id in influencer_ids_list:
                    metrics1.extend(Metrics.scan(Metrics.influencer_id == influencer_id))
                for m in metrics1:
                    metrics_map.setdefault(m.influencer_id, []).append(m.to_dict())
            except Exception as e:
                logging.error(f"Error loading metrics for influencers: {e}")

            def serialize(inf):
                """Serialize influencer data with aggregated metrics and socials."""

                def get_platform_icon(platform_name: str) -> str:
                    return {
                        "instagram": "/instagram.svg",
                        "tiktok": "/tiktok.svg",
                    }.get(platform_name.lower(), "generic")

                def get_socials(inf, metrics_list):
                    socials = []
                    platform_metrics = {m.get("platform"): m for m in metrics_list or []}

                    for p in getattr(inf, "platforms", []):
                        platform_name = getattr(p.platform, "value", getattr(p, "platform", str(p)))
                        handle = getattr(p, "influencer_handle", "") or ""
                        metric = platform_metrics.get(platform_name, {})

                        socials.append({
                            "icon": get_platform_icon(platform_name),
                            "platform": platform_name,
                            "handle": handle,
                            "value": handle,
                            "engagement": f"{metric.get('engagement_rate', 0.0)}%",
                            "followers": format_number_short(metric.get("total_followers", 0)) if metric else "",
                            "likes": format_number_short(metric.get("total_likes", 0)) if metric else "",
                            "posts": metric.get("total_posts", 0) if metric else 0,
                        })
                    return socials

                def summarize_metrics_data(data_list):
                    totals = {
                        "total_followers": 0,
                        "total_likes": 0,
                        "total_posts": 0,
                        "total_comments": 0,
                        "total_shares": 0,
                        "total_views": 0,
                    }

                    platforms = set()
                    max_engagement = 0.0

                    for rec in data_list or []:
                        for key in totals:
                            totals[key] += rec.get(key, 0)
                        if platform := rec.get("platform"):
                            platforms.add(platform)
                        max_engagement = max(max_engagement, rec.get("engagement_rate", 0.0))

                    totals["engagement_rate"] = max_engagement
                    totals["platforms"] = sorted(platforms)
                    return totals

                # --- Compute ---
                influencer_metrics = metrics_map.get(inf.influencer_id, [])
                combined = summarize_metrics_data(influencer_metrics)

                platforms = getattr(inf, "platforms", [])
                default_platform = platforms[0] if platforms else None

                category_attr = getattr(inf, "category", [])
                categories = [category_attr] if isinstance(category_attr, str) else list(category_attr or [])

                # --- Final Output ---
                return {
                    "id": inf.influencer_id,
                    "name": inf.name,
                    "avatar": getattr(default_platform, "profile_img_url", ""),
                    "bio": getattr(default_platform, "influencer_bio", ""),
                    "engagement": f"{combined.get('engagement_rate', 0.0)}%",
                    "reach": format_number_short(combined.get("total_followers", 0)),
                    "totalFollowers": format_number_short(combined.get("total_followers", 0)),
                    "totalLikes": format_number_short(combined.get("total_likes", 0)),
                    "posts": combined.get("total_posts", 0),
                    "categories": categories,
                    "platforms": combined.get("platforms", []),
                    "socials": get_socials(inf, influencer_metrics),
                    "tag": categories[0] if categories else "",
                    "gender": getattr(getattr(inf, "gender", None), "value", None),
                    "recentPosts": getattr(inf, "recent_posts", []),
                    "conversions": combined.get("conversions", 0),
                    "progress": combined.get("progress", 0),
                }

        body = {"success": True, "data": [serialize(inf) for inf in filtered]}
        if out_token:
            body['next_token'] = out_token
        return make_response(jsonify(body), 200)
    except Exception as e:
        logging.error(f"Unexpected error in search_influencers: {e}")
        return make_response(jsonify({'success': False, 'error': 'Unexpected error occurred'}), 500)
