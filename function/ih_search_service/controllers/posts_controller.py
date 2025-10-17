from flask import Blueprint, request, jsonify, make_response
from enums.platform import Platform
from schema.posts import PostSchema
from model.posts import Post
from model.unicode_enum_attribute import UnicodeEnumAttribute
from utils.pagination import paginate_list

bp = Blueprint('posts', __name__)

post_schema = PostSchema()
posts_schema = PostSchema(many=True)


def _paginate_response(result_iterable):
    limit = request.args.get('limit', type=int)
    next_token = request.args.get('next_token', type=str)

    # Support DB-backed return of (iterable, last_key)
    if isinstance(result_iterable, tuple) and len(result_iterable) == 2:
        iterable, last_key = result_iterable
        items = [r for r in iterable]
        token = None
        if last_key:
            from ..utils.pagination import encode_token
            token = encode_token({'type': 'last_key', 'key': last_key})
        return items, token

    items = list(result_iterable)
    if limit is None and next_token is None:
        return items, None
    page_items, out_token = paginate_list(items, limit or 50, next_token)
    return page_items, out_token


def serialize_post(post):
    data = post_schema.dump(post)
    if 'platform' in data and isinstance(post.platform, Platform):
        data['platform'] = UnicodeEnumAttribute(Platform).serialize(post.platform)
    return data


def serialize_posts(posts):
    return [serialize_post(post) for post in posts]


@bp.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    errors = post_schema.validate(data)
    if errors:
        return make_response(jsonify({'success': False, 'error': errors}), 400)
    platform_str = data['platform']
    try:
        platform_enum = Platform(platform_str)
    except ValueError:
        return make_response(jsonify({'success': False, 'error': f'Invalid platform: {platform_str}'}), 400)
    post = Post(
        influencer_id=data['influencer_id'],
        platform=platform_enum,
        title=data['title'],
        url=data['url'],
        description=data.get('description'),
        likes=data.get('likes', 0),
        likes_str=data.get('likes_str'),
        comments=data.get('comments', 0),
        comments_str=data.get('comments_str'),
        shares=data.get('shares', 0),
        shares_str=data.get('shares_str'),
        views=data.get('views', 0),
        views_str=data.get('views_str'),
        post_created_at=data.get('post_created_at'),
        post_type=data.get('post_type')
    )
    post.save_post()
    return make_response(jsonify({'success': True, 'data': serialize_post(post)}), 201)


@bp.route('/posts/<string:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.get_post_by_id(post_id)
    if not post:
        return make_response(jsonify({'success': False, 'error': 'Post not found'}), 404)
    return make_response(jsonify({'success': True, 'data': serialize_post(post)}), 200)


@bp.route('/posts', methods=['GET'])
def get_all_posts():
    limit = request.args.get('limit', type=int)
    next_token = request.args.get('next_token', type=str)
    exclusive_start_key = None
    if next_token:
        try:
            from ..utils.pagination import decode_token
            decoded = decode_token(next_token)
            if isinstance(decoded, dict) and decoded.get('type') == 'last_key':
                exclusive_start_key = decoded.get('key')
        except Exception:
            return make_response(jsonify({'success': False, 'error': 'Invalid next_token'}), 400)
    posts = Post.get_all_posts(limit=limit, exclusive_start_key=exclusive_start_key)
    items, out_token = _paginate_response(posts)
    body = {'success': True, 'data': serialize_posts(items)}
    if out_token:
        body['next_token'] = out_token
    return make_response(jsonify(body), 200)


@bp.route('/posts/<string:post_id>', methods=['PUT'])
def update_post(post_id):
    post = Post.get_post_by_id(post_id)
    if not post:
        return make_response(jsonify({'success': False, 'error': 'Post not found'}), 404)
    data = request.get_json()
    # update supported fields including string formatted metric fields and post metadata
    for field in ['title', 'url', 'description', 
                  'likes', 'likes_str', 'comments', 
                  'comments_str', 'shares', 'shares_str', 
                  'views', 'views_str', 'platform', 
                  'influencer_id', 'post_created_at', 'post_type']:
        if field in data:
            if field == 'platform':
                try:
                    setattr(post, field, Platform(data[field]))
                except ValueError:
                    return make_response(jsonify({'success': False, 'error': f'Invalid platform: {data[field]}'}), 400)
            else:
                setattr(post, field, data[field])
    post.update_post()
    return make_response(jsonify({'success': True, 'data': serialize_post(post)}), 200)


@bp.route('/posts/<string:post_id>', methods=['DELETE'])
def delete_post(post_id):
    success = Post.delete_post_by_id(post_id)
    if not success:
        return make_response(jsonify({'success': False, 'error': 'Post not found'}), 404)
    return make_response(jsonify({'success': True, 'message': 'Post deleted successfully'}), 200)


@bp.route('/posts/search/influencer', methods=['GET'])
def search_posts_by_influencer():
    influencer_id = request.args.get('influencer_id')
    if not influencer_id:
        return make_response(jsonify({'success': False, 'error': 'No influencer_id parameter provided'}), 400)
    limit = request.args.get('limit', type=int)
    next_token = request.args.get('next_token', type=str)
    exclusive_start_key = None
    if next_token:
        try:
            from ..utils.pagination import decode_token
            decoded = decode_token(next_token)
            if isinstance(decoded, dict) and decoded.get('type') == 'last_key':
                exclusive_start_key = decoded.get('key')
        except Exception:
            return make_response(jsonify({'success': False, 'error': 'Invalid next_token'}), 400)
    posts = Post.get_posts_by_influencer_id(influencer_id, limit=limit, exclusive_start_key=exclusive_start_key)
    print(posts)
    items, out_token = _paginate_response(posts)
    body = {'success': True, 'data': serialize_posts(items)}
    if out_token:
        body['next_token'] = out_token
    return make_response(jsonify(body), 200)


@bp.route('/posts/search/url', methods=['GET'])
def search_posts_by_url():
    url = request.args.get('url')
    if not url:
        return make_response(jsonify({'success': False, 'error': 'No url parameter provided'}), 400)
    limit = request.args.get('limit', type=int)
    next_token = request.args.get('next_token', type=str)
    exclusive_start_key = None
    if next_token:
        try:
            from ..utils.pagination import decode_token
            decoded = decode_token(next_token)
            if isinstance(decoded, dict) and decoded.get('type') == 'last_key':
                exclusive_start_key = decoded.get('key')
        except Exception:
            return make_response(jsonify({'success': False, 'error': 'Invalid next_token'}), 400)
    posts = Post.get_posts_by_url(url, limit=limit, exclusive_start_key=exclusive_start_key)
    items, out_token = _paginate_response(posts)
    body = {'success': True, 'data': serialize_posts(items)}
    if out_token:
        body['next_token'] = out_token
    return make_response(jsonify(body), 200)


@bp.route('/posts/search/platform', methods=['GET'])
def search_posts_by_platform():
    platform = request.args.get('platform')
    if not platform:
        return make_response(jsonify({'success': False, 'error': 'No platform parameter provided'}), 400)
    try:
        platform_enum = Platform(platform)
    except ValueError:
        return make_response(jsonify({'success': False, 'error': f'Invalid platform: {platform}'}), 400)
    limit = request.args.get('limit', type=int)
    next_token = request.args.get('next_token', type=str)
    exclusive_start_key = None
    if next_token:
        try:
            from ..utils.pagination import decode_token
            decoded = decode_token(next_token)
            if isinstance(decoded, dict) and decoded.get('type') == 'last_key':
                exclusive_start_key = decoded.get('key')
        except Exception:
            return make_response(jsonify({'success': False, 'error': 'Invalid next_token'}), 400)
    posts = Post.get_posts_by_platform(platform_enum, limit=limit, exclusive_start_key=exclusive_start_key)
    items, out_token = _paginate_response(posts)
    body = {'success': True, 'data': serialize_posts(items)}
    if out_token:
        body['next_token'] = out_token
    return make_response(jsonify(body), 200)
