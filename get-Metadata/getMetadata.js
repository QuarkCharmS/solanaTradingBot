"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
var web3_js_1 = require("@solana/web3.js");
var js_1 = require("@metaplex/js");
var node_fetch_1 = require("node-fetch");
var Raydium = require("@raydium-io/raydium-sdk");
// Connect to the Solana cluster
var connection = new web3_js_1.Connection('https://api.mainnet-beta.solana.com');
// Get the token address
var tokenAddress = process.argv[2];
if (!tokenAddress) {
    console.error('Token address is required as a command-line argument.');
    process.exit(1);
}
// Define the public key of the token metadata account
var tokenMintAddress = new web3_js_1.PublicKey(tokenAddress);
function fetchMetadata() {
    return __awaiter(this, void 0, void 0, function () {
        var metadataPDA, metadataAccount, metadataUri, response, metadataJson, socialMediaLinks, liquidityStatus, error_1;
        var _a;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    _b.trys.push([0, 6, , 7]);
                    return [4 /*yield*/, js_1.programs.metadata.Metadata.getPDA(tokenMintAddress)];
                case 1:
                    metadataPDA = _b.sent();
                    return [4 /*yield*/, js_1.programs.metadata.Metadata.load(connection, metadataPDA)];
                case 2:
                    metadataAccount = _b.sent();
                    metadataUri = metadataAccount.data.data.uri;
                    console.log('Metadata URI:', metadataUri);
                    return [4 /*yield*/, (0, node_fetch_1.default)(metadataUri)];
                case 3:
                    response = _b.sent();
                    return [4 /*yield*/, response.json()];
                case 4:
                    metadataJson = _b.sent();
                    console.log('Metadata JSON:', metadataJson);
                    socialMediaLinks = (_a = metadataJson.attributes) === null || _a === void 0 ? void 0 : _a.filter(function (attribute) { return attribute.trait_type === 'Social Media'; }).map(function (attribute) { return attribute.value; });
                    console.log('Social Media Links:', socialMediaLinks);
                    return [4 /*yield*/, checkLiquidityLockStatus(tokenMintAddress)];
                case 5:
                    liquidityStatus = _b.sent();
                    console.log('Liquidity Locked:', liquidityStatus.locked);
                    console.log('Lock Details:', liquidityStatus.details);
                    return [3 /*break*/, 7];
                case 6:
                    error_1 = _b.sent();
                    console.error('Error fetching metadata:', error_1);
                    return [3 /*break*/, 7];
                case 7: return [2 /*return*/];
            }
        });
    });
}
function checkLiquidityLockStatus(tokenMintAddress) {
    return __awaiter(this, void 0, void 0, function () {
        var poolInfo, error_2;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    return [4 /*yield*/, Raydium.getLiquidityPoolInfo(tokenMintAddress.toBase58())];
                case 1:
                    poolInfo = _a.sent();
                    return [2 /*return*/, {
                            locked: poolInfo.locked, // Boolean indicating if liquidity is locked
                            details: poolInfo.lockDetails // Details about the lock (duration, amount, etc.)
                        }];
                case 2:
                    error_2 = _a.sent();
                    console.error('Error checking liquidity lock status:', error_2);
                    return [2 /*return*/, {
                            locked: false,
                            details: 'Unable to determine liquidity lock status'
                        }];
                case 3: return [2 /*return*/];
            }
        });
    });
}
fetchMetadata();
